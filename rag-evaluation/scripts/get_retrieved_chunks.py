"""
Get retrieved chunks from HippoRAG for given queries.

Prerequisites:
  - pip install hipporag2
  - Embedding model and LLM accessible (configured in .env)

Usage:
  Single query:
    python scripts/get_retrieved_chunks.py "What is the prefrontal cortex projectome?"

  Specify species and top_k:
    python scripts/get_retrieved_chunks.py --species mouse --top-k 10 "What is the prefrontal cortex projectome?"

  Batch queries from JSON file (reads "question" field from each entry):
    python scripts/get_retrieved_chunks.py --species mouse --top-k 10 output/all_qa_merged.json

Output:
  results/get_retrieved_chunks_output_<species>_top<k>.json
"""

import os
import json
import re
import argparse
import multiprocessing
from pathlib import Path
from dotenv import load_dotenv

# Project root directory
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env")

SPECIES_CONFIG = {
    "mouse": {
        "rag_dirs": ["RAG-md-mouse", "RAG-md-docs"],
        "save_dir": "rag-mouse",
    },
    "macaque": {
        "rag_dirs": ["RAG-md-macaque"],
        "save_dir": "rag-macaque",
    },
}


# ============ Markdown chunking (from atlas-assistant) ============

# Tunable parameters
_MAX_CHARS = 1600
_MIN_CHARS = 80
_OVERLAP_CHARS = 120

# Structure recognition regexes
_RE_HEADING = re.compile(r'^\s{0,3}#{1,6}\s+')
_RE_HR = re.compile(r'^\s*([-*_])\1{2,}\s*$')
_RE_LIST = re.compile(r'^\s{0,3}([-*+]|(\d+\.))\s+')
_RE_TABLE_ROW = re.compile(r'^\s*\|?.*\|.*\|?\s*$')
_RE_MATH_FENCE = re.compile(r'^\s*\$\$\s*$')
_RE_IMPORTANT_SHORT = re.compile(
    r'(?i)\b(p\s*[<=>]\s*0?\.\d+|p-?value|n\s*=\s*\d+|auc|f1|accuracy|recall|precision|ci\b|odds|hr\b|'
    r'fold|epoch|lr\s*=|loss|mean\s*\±|±|%)\b'
)


def _split_long(text: str, max_len: int, overlap: int) -> list[str]:
    """Split overly long text (preserving sentence boundaries)"""
    text = text.strip()
    if len(text) <= max_len:
        return [text]

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
                for i in range(0, len(p), max_len):
                    out.append(p[i:i + max_len].strip())

    if buf:
        out.append(buf)

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


def read_markdown_file(file_path: str) -> list[str]:
    """Read a markdown file and split into chunks."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    content = content.replace('\r\n', '\n').replace('\r', '\n')
    content = re.sub(r'\n{3,}', '\n\n', content)

    lines = content.split('\n')

    # Structural block aggregation
    blocks = []
    cur = []
    mode = None
    cur_kind = "text"

    def flush():
        nonlocal cur, cur_kind
        if cur:
            blocks.append(cur)
        cur = []
        cur_kind = "text"

    for raw in lines:
        line = raw.rstrip('\n')

        if not line.strip():
            flush()
            continue

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

        if _RE_MATH_FENCE.match(line):
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

        if _RE_HEADING.match(line):
            flush()
            cur_kind = "heading"
            cur.append(line.strip())
            flush()
            continue

        if _RE_LIST.match(line):
            if cur_kind != "list":
                flush()
                cur_kind = "list"
            cur.append(line.strip())
            continue

        if line.count('|') >= 2 and _RE_TABLE_ROW.match(line):
            if cur_kind != "table":
                flush()
                cur_kind = "table"
            cur.append(line.strip())
            continue

        if cur_kind != "text":
            flush()
            cur_kind = "text"

        if cur and cur[-1].endswith('-') and line[:1].islower():
            cur[-1] = cur[-1][:-1] + line.strip()
        else:
            cur.append(line.strip())

    flush()

    # Merge headings with the following block
    merged = []
    i = 0
    while i < len(blocks):
        b = blocks[i]
        if len(b) == 1 and _RE_HEADING.match(b[0]) and i + 1 < len(blocks):
            merged.append(b + [""] + blocks[i + 1])
            i += 2
        else:
            merged.append(b)
            i += 1

    # Generate the final chunks
    file_tag = f"[source: {os.path.basename(file_path)}]"
    chunks = []

    for b in merged:
        if not b:
            continue

        first = b[0].strip() if b else ""
        is_code = first.startswith("```")
        is_math = _RE_MATH_FENCE.match(first) is not None
        is_list = _RE_LIST.match(first) is not None
        is_table = ('|' in first and first.count('|') >= 2)

        if is_code or is_math:
            text = "\n".join(b).strip()
        elif is_list or is_table:
            text = "\n".join([x.strip() for x in b if x.strip()])
        else:
            text = " ".join([x.strip() for x in b if x.strip()])

        text = _RE_HEADING.sub('', text).strip()

        if not text:
            continue

        if len(text) > _MAX_CHARS and not (is_code or is_math):
            sub = _split_long(text, _MAX_CHARS, _OVERLAP_CHARS)
        else:
            sub = [text]

        for s in sub:
            s = s.strip()
            if not s:
                continue
            if len(s) < _MIN_CHARS and not _RE_IMPORTANT_SHORT.search(s):
                if chunks:
                    chunks[-1] = (chunks[-1] + " " + s).strip()
                else:
                    continue
            else:
                chunks.append(s)

    # Final length check
    final_chunks = []
    for c in chunks:
        if len(c) <= _MAX_CHARS or c.startswith("```") or _RE_MATH_FENCE.match(c or ""):
            final_chunks.append(f"{file_tag} {c}")
        else:
            for s in _split_long(c, _MAX_CHARS, _OVERLAP_CHARS):
                if s.strip():
                    final_chunks.append(f"{file_tag} {s.strip()}")

    return final_chunks


# ============ Document loading ============

def load_docs(data_dir: Path, dir_names: list[str]) -> list[str]:
    """Load and deduplicate documents from specified directories."""
    docs = []
    for dir_name in dir_names:
        rag_md_dir = data_dir / dir_name
        if not rag_md_dir.is_dir():
            print(f"Warning: directory not found: {rag_md_dir}")
            continue
        md_files = sorted(rag_md_dir.glob("*.md"))
        for file_path in md_files:
            try:
                file_docs = read_markdown_file(str(file_path))
                docs.extend([d for d in file_docs if d and isinstance(d, str)])
            except Exception as e:
                print(f"Warning: {file_path.name} load failed: {e}")

    # Deduplicate
    seen = set()
    uniq = []
    for d in docs:
        key = re.sub(r"\s+", " ", d).strip()
        if key and key not in seen:
            seen.add(key)
            uniq.append(d)
    return uniq


def main():
    multiprocessing.freeze_support()

    from hipporag import HippoRAG
    from hipporag.utils.config_utils import BaseConfig

    parser = argparse.ArgumentParser(description="Get retrieved chunks from HippoRAG")
    parser.add_argument("query", help="Query string or path to queries JSON file")
    parser.add_argument("--species", choices=["mouse", "macaque"], required=True,
                        help="Species to query (required)")
    parser.add_argument("--top-k", type=int, default=10,
                        help="Number of top chunks fed to LLM (default: 10)")
    args = parser.parse_args()

    base_url = os.getenv('BASE_URL')
    llm_model = os.getenv('LLM_MODEL', '')
    embedding_model = os.getenv('EMBEDDING_MODEL', '')
    data_dir = ROOT_DIR / "data"

    config = SPECIES_CONFIG[args.species]
    top_k = args.top_k

    global_config = BaseConfig(qa_top_k=top_k)

    hippo = HippoRAG(
        save_dir=str(data_dir / config["save_dir"]),
        llm_model_name=llm_model,
        embedding_model_name=embedding_model,
        llm_base_url=base_url,
        embedding_base_url=base_url,
        global_config=global_config,
    )

    docs = load_docs(data_dir, config["rag_dirs"])
    if docs:
        hippo.index(docs)

    # Determine if arg is a JSON file or a direct query string
    query_path = Path(args.query)
    if query_path.suffix == '.json' and query_path.exists():
        queries_data = json.loads(query_path.read_text(encoding="utf-8"))
        queries = [item['question'] for item in queries_data]
    else:
        queries = [args.query]

    print(f"Species: {args.species}, Top-K: {top_k}, Queries: {len(queries)}")

    # Resume support: check for existing results
    results_dir = ROOT_DIR / "results"
    results_dir.mkdir(exist_ok=True)
    output_path = results_dir / f"get_retrieved_chunks_output_{args.species}_top{top_k}.json"

    results = []
    if output_path.exists():
        results = json.loads(output_path.read_text(encoding="utf-8"))
    done_count = len(results)

    if done_count >= len(queries):
        print(f"Already complete ({done_count}/{len(queries)}), nothing to do.")
        return

    if done_count > 0:
        print(f"Resuming from {done_count}/{len(queries)}")

    for i, query in enumerate(queries[done_count:], done_count + 1):
        solution = hippo.rag_qa(queries=[query])
        qs = solution[0][0]
        entry = {
            "question": qs.question,
            "retrieved_docs": qs.docs[:top_k],
            "doc_scores": [float(s) for s in qs.doc_scores[:top_k]],
            "answer": qs.answer,
        }
        results.append(entry)
        output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{i}/{len(queries)}] Done: {query[:60]}...")

    print(f"\nResults written to {output_path}")


if __name__ == '__main__':
    main()
