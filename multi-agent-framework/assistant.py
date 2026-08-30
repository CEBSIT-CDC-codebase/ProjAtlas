import os
import glob
import json
import random
import types
from typing import List, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv
import httpx
from openai import OpenAI

# Langfuse was removed with the platform switch (no Langfuse host anymore).
# Keep a no-op `observe` decorator so the rest of the code is unchanged.
def observe(*d_args, **d_kwargs):
    def _decorator(func):
        return func
    # Support both @observe and @observe()
    if len(d_args) == 1 and callable(d_args[0]) and not d_kwargs:
        return d_args[0]
    return _decorator

from hipporag import HippoRAG
from hipporag.utils.config_utils import BaseConfig
from hipporag.information_extraction.openie_openai import OpenIE
from hipporag.utils.llm_utils import fix_broken_generated_json, filter_invalid_triples
from hipporag.utils.misc_utils import TripleRawOutput, NerRawOutput
from pprint import pprint
import logging
import re
import time
from datetime import datetime
from contextlib import contextmanager

# Global switch for LLM logging
ENABLE_LLM_LOGGING = False


def _apply_insecure_ssl_patch():
    """Force httpx clients to skip TLS verification (equivalent to `curl -k`).

    HippoRAG constructs its own OpenAI/httpx clients internally without exposing
    a `verify` option, so we patch httpx.Client / httpx.AsyncClient defaults to
    cover every client created in this process. Only used for the self-signed
    internal serving endpoint; disable via DISABLE_SSL_VERIFY=false.
    """
    if getattr(httpx, '_insecure_patched', False):
        return
    import urllib3
    urllib3.disable_warnings()
    _orig_client_init = httpx.Client.__init__
    _orig_async_init = httpx.AsyncClient.__init__

    def _client_init(self, *args, **kwargs):
        kwargs['verify'] = False
        _orig_client_init(self, *args, **kwargs)

    def _async_init(self, *args, **kwargs):
        kwargs['verify'] = False
        _orig_async_init(self, *args, **kwargs)

    httpx.Client.__init__ = _client_init
    httpx.AsyncClient.__init__ = _async_init
    httpx._insecure_patched = True

@contextmanager
def timer(description: str = "Operation", print_times: bool = True):
    """Context manager for measuring code block execution time.

    - Uses time.perf_counter() for higher resolution and stability.
    - Optionally prints wall-clock start/end times (datetime.now).
    """
    start_perf = time.perf_counter()
    start_datetime = datetime.now()
    try:
        yield
    finally:
        end_perf = time.perf_counter()
        end_datetime = datetime.now()
        duration = end_perf - start_perf

        if print_times:
            print(f"\n{description} start: {start_datetime.isoformat(sep=' ', timespec='microseconds')}")
            print(f"{description} end: {end_datetime.isoformat(sep=' ', timespec='microseconds')}")
        print(f"{description} duration: {duration:.6f}s")



class LoggingOpenAIClient:
    """OpenAI client wrapper that automatically logs all LLM call inputs and outputs."""
    def __init__(self, client, logger):
        self.client = client
        self.logger = logger
        self.chat = LoggingOpenAIClient.ChatWrapper(client.chat, logger)
    class ChatWrapper:
        def __init__(self, chat, logger):
            self.chat = chat
            self.logger = logger
            self.completions = LoggingOpenAIClient.CompletionsWrapper(chat.completions, logger)
    class CompletionsWrapper:
        def __init__(self, completions, logger):
            self.completions = completions
            self.logger = logger
        def create(self, **kwargs):
            if ENABLE_LLM_LOGGING:
                self.logger.info("\n--- LLM Call - Request ---")
                self.logger.info(f"Model: {kwargs.get('model', 'unknown')}")
                self.logger.info(f"Messages: {json.dumps(kwargs.get('messages', []), indent=2, ensure_ascii=False)}")
                if kwargs.get('tools'):
                    self.logger.info(f"Tools: {json.dumps(kwargs.get('tools'), indent=2, ensure_ascii=False)}")
                self.logger.info("------\n")
            response = self.completions.create(**kwargs)
            if ENABLE_LLM_LOGGING:
                self.logger.info("\n--- LLM Call - Response ---")
                if hasattr(response.choices[0].message, 'content') and response.choices[0].message.content:
                    self.logger.info(f"Content: {response.choices[0].message.content}")
                if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
                    self.logger.info(f"Tool calls: {[t.to_dict() for t in response.choices[0].message.tool_calls]}")
                self.logger.info("------\n")
            return response

def read_sentences_from_file(file_path: str) -> List[str]:
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def read_markdown_file(file_path: str) -> List[str]:
    """
    Markdown chunking strategy (requires md_cleaner preprocessing):
    - Focus on structure recognition and reasonable splitting
    - Preserve all academic-related content
    - Simplified cleaning logic
    """
    # ===== Tunable parameters =====
    MAX_CHARS = 1600  # chunk upper limit
    MIN_CHARS = 80  # chunk lower limit
    OVERLAP_CHARS = 120  # overlap for long text splitting

    # ===== Structure recognition regex =====
    RE_HEADING = re.compile(r'^\s{0,3}#{1,6}\s+')
    RE_HR = re.compile(r'^\s*([-*_])\1{2,}\s*$')
    RE_LIST = re.compile(r'^\s{0,3}([-*+]|(\d+\.))\s+')
    RE_TABLE_ROW = re.compile(r'^\s*\|?.*\|.*\|?\s*$')
    RE_MATH_FENCE = re.compile(r'^\s*\$\$\s*$')

    # Important short lines (statistics, etc.)
    RE_IMPORTANT_SHORT = re.compile(
        r'(?i)\b(p\s*[<=>]\s*0?\.\d+|p-?value|n\s*=\s*\d+|auc|f1|accuracy|recall|precision|ci\b|odds|hr\b|'
        r'fold|epoch|lr\s*=|loss|mean\s*\±|±|%)\b'
    )

    def _split_long(text: str, max_len: int, overlap: int) -> List[str]:
        """Split long text while preserving sentence boundaries."""
        text = text.strip()
        if len(text) <= max_len:
            return [text]

        # Sentence boundaries
        sent_end = re.compile(r'(?<=[。！？.!?])\s+')
        parts = sent_end.split(text)
        out = []
        buf = ""

        for p in parts:
            if not p:
                continue
            candidate = (buf + " " + p).strip() if buf else p.strip()
            if len(candidate) <= max_len:
                buf = candidate
            else:
                if buf:
                    out.append(buf)
                    buf = p.strip()
                else:
                    # Hard split
                    for i in range(0, len(p), max_len):
                        out.append(p[i:i + max_len].strip())

        if buf:
            out.append(buf)

        # Overlap processing
        if overlap > 0 and len(out) > 1:
            overlapped = []
            for i, chunk in enumerate(out):
                if i == 0:
                    overlapped.append(chunk)
                    continue
                prev = overlapped[-1]
                tail = prev[-overlap:] if len(prev) > overlap else prev
                overlapped.append((tail + " " + chunk).strip())
            return overlapped

        return out

    # ===== Read file =====
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Basic normalization (md_cleaner already does deep cleaning, only simple processing here)
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    content = re.sub(r'\n{3,}', '\n\n', content)  # Merge excessive blank lines

    lines = content.split('\n')

    # ===== Structural block aggregation =====
    blocks = []
    cur = []
    mode = None  # None / 'code' / 'math'
    cur_kind = "text"

    def flush():
        nonlocal cur, cur_kind
        if cur:
            blocks.append(cur)
        cur = []
        cur_kind = "text"

    for raw in lines:
        line = raw.rstrip('\n')

        # Empty line -> paragraph boundary
        if not line.strip():
            flush()
            continue

        # Code block and math block detection
        if line.strip().startswith("```"):
            if mode == "code":
                cur.append(line)
                flush()
                mode = None
            else:
                flush()
                mode = "code"
                cur_kind = "code"
                cur.append(line)
            continue

        if RE_MATH_FENCE.match(line):
            if mode == "math":
                cur.append(line)
                flush()
                mode = None
            else:
                flush()
                mode = "math"
                cur_kind = "math"
                cur.append(line)
            continue

        if mode in ("code", "math"):
            cur.append(line)
            continue

        # Structure recognition
        if RE_HEADING.match(line):
            flush()
            cur_kind = "heading"
            cur.append(line.strip())
            flush()  # Heading as standalone block
            continue

        if RE_LIST.match(line):
            if cur_kind != "list":
                flush()
                cur_kind = "list"
            cur.append(line.strip())
            continue

        # Table detection
        if line.count('|') >= 2 and RE_TABLE_ROW.match(line):
            if cur_kind != "table":
                flush()
                cur_kind = "table"
            cur.append(line.strip())
            continue

        # Plain text + hyphenation fix
        if cur_kind != "text":
            flush()
            cur_kind = "text"

        # Hyphenation repair
        if cur and cur[-1].endswith('-') and line[:1].islower():
            cur[-1] = cur[-1][:-1] + line.strip()
        else:
            cur.append(line.strip())

    flush()

    # ===== Merge heading with next block =====
    merged = []
    i = 0
    while i < len(blocks):
        b = blocks[i]
        if len(b) == 1 and RE_HEADING.match(b[0]) and i + 1 < len(blocks):
            merged.append(b + [""] + blocks[i + 1])
            i += 2
        else:
            merged.append(b)
            i += 1

    # ===== Generate final chunks =====
    file_tag = f"[source: {os.path.basename(file_path)}]"
    chunks = []

    for b in merged:
        if not b:
            continue

        first = b[0].strip() if b else ""
        is_code = first.startswith("```")
        is_math = RE_MATH_FENCE.match(first) is not None
        is_list = RE_LIST.match(first) is not None
        is_table = ('|' in first and first.count('|') >= 2)

        if is_code or is_math:
            text = "\n".join(b).strip()
        elif is_list or is_table:
            text = "\n".join([x.strip() for x in b if x.strip()])
        else:
            text = " ".join([x.strip() for x in b if x.strip()])

        # Remove heading markers
        text = RE_HEADING.sub('', text).strip()

        if not text:
            continue

        # Split long text
        if len(text) > MAX_CHARS and not (is_code or is_math):
            sub = _split_long(text, MAX_CHARS, OVERLAP_CHARS)
        else:
            sub = [text]

        for s in sub:
            s = s.strip()
            if not s:
                continue

            # Short line handling: keep important short lines, merge ordinary ones
            if len(s) < MIN_CHARS and not RE_IMPORTANT_SHORT.search(s):
                if chunks:
                    chunks[-1] = (chunks[-1] + " " + s).strip()
                else:
                    continue
            else:
                chunks.append(s)

    # Final length check
    final_chunks = []
    for c in chunks:
        if len(c) <= MAX_CHARS or c.startswith("```") or RE_MATH_FENCE.match(c or ""):
            final_chunks.append(f"{file_tag} {c}")
        else:
            for s in _split_long(c, MAX_CHARS, OVERLAP_CHARS):
                if s.strip():
                    final_chunks.append(f"{file_tag} {s.strip()}")

    print(f"Debug: file {os.path.basename(file_path)} split into {len(final_chunks)} chunks")
    return final_chunks


# Monkey patch: fix potential bug in HippoRAG where OpenIE may return non-string entity types

def patched_save_openie_results(self, all_openie_info):
    if ENABLE_LLM_LOGGING:
        print("\n[Patch] Checking and fixing non-string data in OpenIE results...")

    fixed_count = 0
    for chunk in all_openie_info:
        if 'extracted_entities' in chunk:
            original_entities = chunk['extracted_entities']
            cleaned_entities = []
            for e in original_entities:
                if isinstance(e, str):
                    cleaned_entities.append(e)
                elif isinstance(e, (int, float)):
                    cleaned_entities.append(str(e))
                    fixed_count += 1
                elif e is not None:
                    cleaned_entities.append(str(e))
                    fixed_count += 1
            chunk['extracted_entities'] = cleaned_entities

    if fixed_count > 0:
        print(f"[Patch] Fixed {fixed_count} non-string entities that would cause crashes!")

    return HippoRAG.save_openie_results(self, all_openie_info)


# Monkey patch: HippoRAG's triple_extraction only recognizes a raw
# `{"triples": [...]}` object. Our LLM (mistral-small) often wraps that in a
# ```json code fence, or emits a value containing '[' / ']' that breaks the
# original regex, so many chunks fail with "'NoneType' object has no attribute
# 'group'" and get zero triples. This patch tries the same regex first, then
# falls back to stripping code fences and parsing the JSON directly.

def _lenient_extract_triples(real_response):
    pattern = r'\{[^{}]*"triples"\s*:\s*\[[^\]]*\][^{}]*\}'
    match = re.search(pattern, real_response, re.DOTALL)
    if match is not None:
        return eval(match.group())["triples"]

    # Fallback: strip ```json / ``` fences and any leading/trailing prose,
    # then parse the first {...} block as JSON.
    text = real_response.strip()
    text = re.sub(r'^```(?:json)?', '', text.strip(), flags=re.IGNORECASE).strip()
    text = re.sub(r'```$', '', text.strip()).strip()
    brace_match = re.search(r'\{.*\}', text, re.DOTALL)
    if brace_match is None:
        raise ValueError(f"No JSON object found in response: {real_response[:200]!r}")
    return json.loads(brace_match.group())["triples"]


def patched_triple_extraction(self, chunk_key, passage, named_entities):
    messages = self.prompt_template_manager.render(
        name='triple_extraction',
        passage=passage,
        named_entity_json=json.dumps({"named_entities": named_entities}),
    )

    raw_response = ""
    metadata = {}
    try:
        raw_response, metadata, cache_hit = self.llm_model.infer(messages=messages)
        metadata['cache_hit'] = cache_hit
        if metadata['finish_reason'] == 'length':
            real_response = fix_broken_generated_json(raw_response)
        else:
            real_response = raw_response
        extracted_triples = _lenient_extract_triples(real_response)
        triplets = filter_invalid_triples(triples=extracted_triples)
    except Exception as e:
        if ENABLE_LLM_LOGGING:
            print(f"[Patch] Exception for chunk {chunk_key}: {e}")
        metadata.update({'error': str(e)})
        return TripleRawOutput(chunk_id=chunk_key, response=raw_response, metadata=metadata, triples=[])

    return TripleRawOutput(chunk_id=chunk_key, response=raw_response, metadata=metadata, triples=triplets)


@dataclass
class AssistantMessage:
    content: str = ""
    tool_calls: List[str] = field(default_factory=list)

@dataclass
class UserInput:
    id: str = ""
    task: str = ""
    content: str = ""
    neurons: List[Any] = field(default_factory=list)
    regions: List[Any] = field(default_factory=list)
    matrix: List[Any] = field(default_factory=list)

def process_tool_calls(response, assistant_message):
    """Process tool call responses."""
    tool_calls = response.choices[0].message.tool_calls
    if tool_calls:
        assistant_message.tool_calls = [t.to_dict() for t in tool_calls]
        # turn arguments into dict if any
        for call in assistant_message.tool_calls:
            if call.get('function', {}).get('arguments'):
                call['function']['arguments'] = json.loads(call['function']['arguments'])
    else:
        # Check if response content is valid JSON format
        try:
            json_content = json.loads(response.choices[0].message.content)
            # If JSON format, convert to tool_calls
            wraps = []
            for i, func in enumerate(json_content):
                # rename parameters if any, to arguments 
                if func.get('parameters'):
                    func['arguments'] = func['parameters']
                    del func['parameters']
                dump_str = json.dumps({
                    'id': 'call_' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8)),
                    'index': i,
                    'type': 'function',
                    'function': func,
                })
                wraps.append(dump_str.replace('\\\\\\', '\\'))
            assistant_message.tool_calls = wraps
        except json.JSONDecodeError:
            # If not JSON format, keep as-is
            assistant_message.content = response.choices[0].message.content

class ChatSession:
    def __init__(self):
        """Initialize chat session"""
        # Load .env from this file's directory, not the current working dir, so
        # `python -m atlas-assistant.assistant` (run from the parent dir) still
        # picks it up. Without this, BASE_URL/API_KEY end up empty and every
        # LLM call fails silently -> zero entities -> ZeroDivisionError on index.
        load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
        self.base_url = os.getenv('BASE_URL')
        self.embedding_base_url = os.getenv('EMBEDDING_BASE_URL', self.base_url)
        self.api_key = os.getenv('API_KEY', '')
        # HippoRAG builds its own OpenAI clients internally and reads the key
        # from the environment, so propagate it there too.
        if self.api_key:
            os.environ['OPENAI_API_KEY'] = self.api_key

        # The serving endpoint uses a self-signed TLS root. When verification is
        # disabled, patch httpx so every client in the process (including the
        # ones HippoRAG creates internally) skips certificate checks.
        self.verify_ssl = os.getenv('DISABLE_SSL_VERIFY', 'false').lower() not in ('true', '1', 'yes')
        if not self.verify_ssl:
            _apply_insecure_ssl_patch()

        self.llm_model = os.getenv('LLM_MODEL', '')
        self.embedding_model = os.getenv('EMBEDDING_MODEL', '')
        self.function_calling_model = os.getenv('FUNCTION_CALLING_MODEL', '')
        self.sessions = {}  # Store sessions for different users

        # Initialize logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # Avoid adding duplicate handlers
        if not self.logger.handlers:
            file_handler = logging.FileHandler('assistant.log', mode='a', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
        if ENABLE_LLM_LOGGING:
            self.logger.info("ChatSession initialized and logging is configured.")

        # Use wrapper client to automatically log all LLM calls
        original_client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            http_client=httpx.Client(verify=self.verify_ssl),
        )
        self.client = LoggingOpenAIClient(original_client, self.logger)

        # Initialize two independent HippoRAG instances: mouse and macaque with separate indices
        data_dir = os.path.join(os.path.dirname(__file__), 'data')

        # Mouse HippoRAG (retrieves from RAG-md-mouse + RAG-md-docs)
        # Each instance needs its own BaseConfig: HippoRAG mutates global_config
        # during init (save_dir derived paths), so a shared object lets the
        # macaque instance overwrite the mouse one's settings.
        self.hipporag = HippoRAG(
            save_dir=os.path.join(data_dir, 'rag-mouse'),
            llm_model_name=self.llm_model,
            embedding_model_name=self.embedding_model,
            llm_base_url=self.base_url,
            embedding_base_url=self.embedding_base_url,
            embedding_api_key=self.api_key,
            llm_api_key=self.api_key,
            global_config=BaseConfig(qa_top_k=10),
        )
        self.hipporag.save_openie_results = types.MethodType(patched_save_openie_results, self.hipporag)
        self.hipporag.openie.triple_extraction = types.MethodType(patched_triple_extraction, self.hipporag.openie)

        # Macaque HippoRAG (retrieves from RAG-md-macaque + RAG-md-docs)
        self.hipporag_macaque = HippoRAG(
            save_dir=os.path.join(data_dir, 'rag-macaque'),
            llm_model_name=self.llm_model,
            embedding_model_name=self.embedding_model,
            llm_base_url=self.base_url,
            embedding_base_url=self.embedding_base_url,
            embedding_api_key=self.api_key,
            llm_api_key=self.api_key,
            global_config=BaseConfig(qa_top_k=10),
        )
        self.hipporag_macaque.save_openie_results = types.MethodType(patched_save_openie_results, self.hipporag_macaque)
        self.hipporag_macaque.openie.triple_extraction = types.MethodType(patched_triple_extraction, self.hipporag_macaque.openie)
        self.logger.info("Applied HippoRAG type safety patch")

        # Load mouse RAG documents (RAG-md-mouse + RAG-md-docs)
        mouse_docs = self._load_rag_docs(data_dir, ['RAG-md-mouse', 'RAG-md-docs'])
        if mouse_docs:
            self.logger.info(f"Building mouse RAG index, total chunks: {len(mouse_docs)}")
            try:
                self.hipporag.index(mouse_docs)
                self.logger.info("Mouse RAG index built successfully")
            except Exception as e:
                self.logger.error(f"Critical error building mouse index: {e}", exc_info=True)
        else:
            self.logger.warning("No mouse documents loaded, mouse RAG will be unavailable")

        # Load macaque RAG documents (RAG-md-macaque)
        macaque_docs = self._load_rag_docs(data_dir, ['RAG-md-macaque'])
        if macaque_docs:
            self.logger.info(f"Building macaque RAG index, total chunks: {len(macaque_docs)}")
            try:
                self.hipporag_macaque.index(macaque_docs)
                self.logger.info("Macaque RAG index built successfully")
            except Exception as e:
                self.logger.error(f"Critical error building macaque index: {e}", exc_info=True)
        else:
            self.logger.warning("No macaque documents loaded, macaque RAG will be unavailable")

    def _load_rag_docs(self, data_dir: str, dir_names: List[str]) -> List[str]:
        """Load all MD files from specified directories and deduplicate."""
        docs = []
        for dir_name in dir_names:
            rag_md_dir = os.path.join(data_dir, dir_name)
            if not os.path.isdir(rag_md_dir):
                self.logger.warning(f"[{dir_name}] Directory not found: {rag_md_dir}")
                continue
            md_files = [f for f in os.listdir(rag_md_dir) if f.lower().endswith('.md')]
            if md_files:
                self.logger.info(f"[{dir_name}] Found {len(md_files)} MD files, loading...")
                for filename in md_files:
                    file_path = os.path.join(rag_md_dir, filename)
                    try:
                        file_docs = read_markdown_file(file_path)
                        valid_docs = [str(d) for d in file_docs if d and isinstance(d, str)]
                        docs.extend(valid_docs)
                        self.logger.debug(f"{filename}: {len(valid_docs)} valid chunks")
                    except Exception as e:
                        self.logger.error(f"{filename} load failed: {e}")
            else:
                self.logger.warning(f"[{dir_name}] No MD files found in directory")

        if docs:
            seen = set()
            uniq = []
            for d in docs:
                key = re.sub(r"\s+", " ", d).strip()
                if key and key not in seen:
                    seen.add(key)
                    uniq.append(d)
            docs = uniq
        return docs

    def get_user_session(self, user_id):
        if user_id not in self.sessions:
            self.sessions[user_id] = {"messages": [], "tool_calls_indices": []}
        return self.sessions[user_id]


    @observe()
    def send_message(self, user_input: UserInput) -> AssistantMessage:
        """
        Send user message and get response.
        :param user_input: User input text
        :return: AI assistant response
        """
        session = self.get_user_session(user_input.id)
        assistant_message = AssistantMessage()
        try:
            # Paper task with HippoRAG
            if user_input.task == "paper" and self.hipporag:
                if ENABLE_LLM_LOGGING:
                    self.logger.info("\n--- paper: query sent to hipporag ---")
                    self.logger.info(f"Query: {user_input.content}")
                    self.logger.info("------\n")

                solution = self.hipporag.rag_qa(queries=[user_input.content])
                session["messages"].append({"role": "user", "content": user_input.content})
                qs = solution[0][0]
                assistant_message.content = qs.answer

                if ENABLE_LLM_LOGGING:
                    self.logger.info("\n--- paper: hipporag response ---")
                    self.logger.info(f"Response: {qs.answer}")
                    self.logger.info("------\n")
            elif user_input.task == "form":
                from .function_calling.form import get_form_functions
                functions = get_form_functions()
                cutOff = -1
                if session['tool_calls_indices']:
                    cutOff = session['tool_calls_indices'][-1]
                session["messages"].append({"role": "user", "content": user_input.content})
                # Create message list with system prompt first
                messages = [{
                    "role": "system",
                    "content": "You are a helpful assistant that processes queries about neurons and brain regions. When responding, use the provided functions to query or manipulate data. Always do function calling when appropriate."
                }]
                messages.extend(session["messages"][cutOff + 1:])

                response = self.client.chat.completions.create(
                    model=self.function_calling_model,
                    messages=messages,
                    tools=functions,
                )
                process_tool_calls(response, assistant_message)
            elif user_input.task == "paper-macaque" and self.hipporag_macaque:
                if ENABLE_LLM_LOGGING:
                    self.logger.info("\n--- paper-macaque: query sent to hipporag ---")
                    self.logger.info(f"Query: {user_input.content}")
                    self.logger.info("------\n")

                solution = self.hipporag_macaque.rag_qa(queries=[user_input.content])
                session["messages"].append({"role": "user", "content": user_input.content})
                qs = solution[0][0]
                assistant_message.content = qs.answer

                if ENABLE_LLM_LOGGING:
                    self.logger.info("\n--- paper-macaque: hipporag response ---")
                    self.logger.info(f"Response: {qs.answer}")
                    self.logger.info("------\n")
            elif user_input.task == "form-macaque":
                from .function_calling.form_macaque import get_form_functions
                functions = get_form_functions()
                cutOff = -1
                if session['tool_calls_indices']:
                    cutOff = session['tool_calls_indices'][-1]
                session["messages"].append({"role": "user", "content": user_input.content})
                messages = [{
                    "role": "system",
                    "content": "You are a helpful assistant that processes queries about neurons and brain regions in macaque. When responding, use the provided functions to query or manipulate data. Always do function calling when appropriate."
                }]
                messages.extend(session["messages"][cutOff + 1:])

                response = self.client.chat.completions.create(
                    model=self.function_calling_model,
                    messages=messages,
                    tools=functions,
                )
                process_tool_calls(response, assistant_message)
            elif user_input.task == "neuroviz":
                from .function_calling.neuroviz import get_neuroviz_functions
                functions = get_neuroviz_functions()
                cutOff = -1
                if session['tool_calls_indices']:
                    cutOff = session['tool_calls_indices'][-1]
                session["messages"].append({"role": "user", "content": user_input.content})
                # Create message list with system prompt first
                messages = [{
                    "role": "system",
                    "content": "You are a helpful assistant that processes requests about visualization of neurons and brain regions. When responding, use the provided functions to manipulation, including camera controls, visual properties etc. Always do function calling when appropriate."
                }]
                messages.extend(session["messages"][cutOff + 1:])

                response = self.client.chat.completions.create(
                    model=self.function_calling_model,
                    messages=messages,
                    tools=functions,
                )
                process_tool_calls(response, assistant_message)
            elif user_input.task == "summarization/viewport":
                from .summarization.viewport import generate_viewport_summary_prompt
                prompt = generate_viewport_summary_prompt(user_input.neurons, user_input.regions)

                # Create message list with user's full prompt
                messages = [{"role": "user", "content": prompt}]
                response = self.client.chat.completions.create(
                    model=self.llm_model,
                    messages=messages,
                )
                assistant_message.content = response.choices[0].message.content
                session["messages"].append({"role": "user", "content": prompt})
            elif user_input.task == "summarization/projection_heatmap_by_axon_length":
                from .summarization.projection_heatmap_by_axon_length import projection_heatmap_by_axon_length
                prompt = projection_heatmap_by_axon_length(user_input.matrix)

                # Create message list with user's full prompt
                messages = [{"role": "user", "content": prompt}]
                response = self.client.chat.completions.create(
                    model=self.llm_model,
                    messages=messages
                )
                assistant_message.content = response.choices[0].message.content
                session["messages"].append({"role": "user", "content": prompt})
            elif user_input.task == "summarization/projection_heatmap_by_terminal_points":
                from .summarization.projection_heatmap_by_terminal_points import projection_heatmap_by_terminal_points
                prompt = projection_heatmap_by_terminal_points(user_input.matrix)

                # Create message list with user's full prompt
                messages = [{"role": "user", "content": prompt}]
                response = self.client.chat.completions.create(
                    model=self.llm_model,
                    messages=messages,
                )
                assistant_message.content = response.choices[0].message.content
                session["messages"].append({"role": "user", "content": prompt})
            elif user_input.task == "summarization/projection":
                from .summarization.projection import generate_projection_prompt
                prompt = generate_projection_prompt(user_input.regions)
                # Create message list with user's full prompt
                messages = [{"role": "user", "content": prompt}]
                response = self.client.chat.completions.create(
                    model=self.llm_model,
                    messages=messages,
                )
                assistant_message.content = response.choices[0].message.content
                session["messages"].append({"role": "user", "content": prompt})
            elif user_input.task == "summarization/soma_distribution":
                from .summarization.soma_distribution import generate_soma_distribution_prompt
                prompt = generate_soma_distribution_prompt(user_input.regions)
                messages = [{"role": "user", "content": prompt}]
                response = self.client.chat.completions.create(
                    model=self.llm_model,
                    messages=messages,
                )
                assistant_message.content = response.choices[0].message.content
                session["messages"].append({"role": "user", "content": prompt})
            else:
                session["messages"].append({"role": "user", "content": user_input.content})
                response = self.client.chat.completions.create(
                    model=self.llm_model,
                    messages=session["messages"]
                )
                assistant_message.content = response.choices[0].message.content
            
            # Append assistant response to history
            session["messages"].append({"role": "assistant", "content": assistant_message.content})
            if assistant_message.tool_calls:
                session["tool_calls_indices"].append(len(session["messages"]) - 1)
            return assistant_message
        except Exception as e:
            self.logger.error(f"Error occurred: {str(e)}", exc_info=True)
            # Always return an AssistantMessage. Returning a bare string here made
            # callers crash on result.content, which masked the original error.
            assistant_message.content = f"Error occurred: {str(e)}"
            return assistant_message
    
    def clear_history(self, user_id: str = "default"):
        """Clear chat history for a given user."""
        if user_id in self.sessions:
            self.sessions[user_id]["messages"] = []
