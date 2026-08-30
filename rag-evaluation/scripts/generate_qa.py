"""
RAG QA data generation script
Uses DeepSeek-V4-Pro to generate QA pairs from paper markdown files
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import anthropic

load_dotenv(Path(__file__).parent.parent / ".env")

# ============ Configuration ============
# Project root directory
ROOT_DIR = Path(__file__).parent.parent

# Read which config group to use from the .env ACTIVE_MODEL setting
ACTIVE_MODEL = os.getenv("ACTIVE_MODEL", "deepseek").lower()

# Load the corresponding key/url/model based on ACTIVE_MODEL
_prefix = ACTIVE_MODEL.upper()
API_KEY = os.getenv(f"{_prefix}_API_KEY", "")
BASE_URL = os.getenv(f"{_prefix}_BASE_URL", "")
MODEL = os.getenv(f"{_prefix}_MODEL", "")

# Document directories
MOUSE_DOC_DIR = ROOT_DIR / "data" / "RAG-md-mouse"
MACAQUE_DOC_DIR = ROOT_DIR / "data" / "RAG-md-macaque"

# Output directories
OUTPUT_DIR = ROOT_DIR / "output"
LOG_DIR = ROOT_DIR / "logs"

# ============ QA generation prompt ============
SYSTEM_PROMPT = "You are a scientific paper QA generator. Strictly follow the format and constraints in the user's instructions. Do not add extra explanations."

QA_PROMPT_TEMPLATE = """Generate high-quality QA pairs from the following paper for RAG system evaluation.

[Task] Generate {single_count} single-evidence QA + {multi_count} multi-evidence QA, {total_count} in total.

[Definitions]
- single-evidence: Can be fully answered by a single sentence from the paper.
- multi-evidence: Requires combining at least two sentences from different paragraphs/sections to fully answer. Neither evidence alone is sufficient.

[Constraints]
1. Questions must be standalone queries. Do NOT use phrases like "this paper", "this study", "the authors", or any language indicating a paper is being referenced.
2. Questions must have definitive answers (closed-ended). No open-ended or subjective questions.
3. Answers: 1-3 sentences, synthesizing evidence. Do NOT copy evidence verbatim.
4. Evidence must be complete sentences from the original text. No truncation (no "...").
5. All content must be based solely on the paper. No external knowledge.

[Critical rule for multi-evidence]
The following are FORBIDDEN as two Evidences:
- Adjacent or consecutive sentences from the same paragraph
- Splitting a single sentence
- Creating "pseudo multi-evidence" by omitting parts of continuous text

The two Evidences MUST come from different sections or paragraphs, separated by multiple sentences.

[Output format] Strictly follow this format for each QA, separated by blank lines:

Q: [question]
A: [answer]
Type: single-evidence
Source:
  - Evidence 1: [complete sentence from original text]

Q: [question]
A: [answer]
Type: multi-evidence
Source:
  - Evidence 1: [complete sentence from original text]
  - Evidence 2: [complete sentence from a different paragraph]

---
Paper content:

{paper_content}
"""

# Splitting threshold (bytes)
SPLIT_THRESHOLD = 30000


def load_document(filepath: Path) -> str:
    """Read a markdown document"""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def strip_references(content: str) -> str:
    """Remove the References section from the paper (only that section, keeping the content before/after it)"""
    # Match # References or ## References (case-insensitive)
    pattern = r"^(#{1,2})\s+[Rr][Ee][Ff][Ee][Rr][Ee][Nn][Cc][Ee][Ss]?\s*$"
    match = re.search(pattern, content, re.MULTILINE)
    if not match:
        return content

    ref_start = match.start()
    heading_level = match.group(1)  # '#' or '##'

    # Find the position of the next heading at the same or higher level
    rest = content[match.end():]
    next_heading = re.search(rf"^{re.escape(heading_level)}\s+", rest, re.MULTILINE)

    if next_heading:
        ref_end = match.end() + next_heading.start()
        return content[:ref_start].rstrip() + "\n\n" + content[ref_end:]
    else:
        # References is the last section, truncate directly
        return content[:ref_start].rstrip()


def split_document(content: str, max_parts: int = 4) -> list[str]:
    """
    Dynamically split the document by headings.
    Number of parts = (KB size after removing references) / 30 + 1 (rounded down), capped by max_parts.
    Split at heading positions, aiming for even distribution.

    Args:
        content: document content with references removed
        max_parts: maximum number of parts (default 4 for mouse, unlimited for macaque)
    """
    size = len(content.encode("utf-8"))

    if size < SPLIT_THRESHOLD:
        return [content]

    num_parts = min(size // 30000 + 1, max_parts)

    # Find all heading positions (# or ##, excluding ### and deeper levels)
    heading_positions = [m.start() for m in re.finditer(r"^#{1,2}\s+", content, re.MULTILINE)]

    if len(heading_positions) < num_parts:
        return [content]

    # Compute ideal split points
    total_len = len(content)
    parts = []
    prev_pos = 0

    for i in range(1, num_parts):
        target = total_len * i // num_parts
        # Find the heading position closest to target
        best_pos = min(heading_positions, key=lambda p: abs(p - target))
        # Avoid extreme splits (any part < 10%)
        if best_pos <= prev_pos or best_pos < total_len * 0.1:
            continue
        parts.append(content[prev_pos:best_pos].rstrip())
        prev_pos = best_pos

    # Last part
    parts.append(content[prev_pos:].lstrip())

    # If splitting failed (only 1 part), return the original text
    return parts if len(parts) > 1 else [content]


def strip_reasoning(content: str) -> str:
    """
    DeepSeek reasoning models prepend a COT reasoning process before the reply.
    In the OpenAI-compatible API, reasoning_content and content are separate fields,
    but if they end up mixed together, manual extraction is needed.
    """
    # If content contains <think>...</think> tags, remove them
    pattern = r"<think>.*?</think>"
    cleaned = re.sub(pattern, "", content, flags=re.DOTALL)
    return cleaned.strip()


def save_log(doc_name: str, messages: list[dict], reasoning: str | None, content: str):
    """Save the complete input/output log, including the COT reasoning process"""
    LOG_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOG_DIR / f"{timestamp}_{doc_name[:30]}.md"

    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"# API Call Log\n\n")
        f.write(f"- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- Model: {MODEL}\n")
        f.write(f"- Document: {doc_name}\n\n")

        f.write(f"## Input (Messages)\n\n")
        for msg in messages:
            f.write(f"### Role: {msg['role']}\n\n")
            f.write(f"```\n{msg['content']}\n```\n\n")

        if reasoning:
            f.write(f"## COT Reasoning Process ({len(reasoning)} characters)\n\n")
            f.write(f"```\n{reasoning}\n```\n\n")

        f.write(f"## Final Output ({len(content)} characters)\n\n")
        f.write(f"```\n{content}\n```\n")

    print(f"Full log saved: {log_path}")
    return log_path


def call_llm(paper_content: str, doc_name: str = "", single_count: int = 10, multi_count: int = 8) -> str:
    """Call the LLM to generate QA, automatically choosing OpenAI-compatible or native Anthropic format based on ACTIVE_MODEL"""
    total_count = single_count + multi_count
    prompt = QA_PROMPT_TEMPLATE.format(
        paper_content=paper_content,
        single_count=single_count,
        multi_count=multi_count,
        total_count=total_count,
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    print(f"Calling {MODEL}, please wait...")

    if ACTIVE_MODEL == "anthropic":
        content, reasoning = _call_anthropic(prompt)
    else:
        content, reasoning = _call_openai_compatible(messages)

    if reasoning:
        print(f"[Reasoning process: {len(reasoning)} characters, automatically separated]")

    # Save the complete log
    save_log(doc_name, messages, reasoning, content)

    # Extra cleanup: in case a <think> tag ended up mixed into content
    content = strip_reasoning(content)

    return content


def _call_openai_compatible(messages: list[dict]) -> tuple[str, str | None]:
    """OpenAI-compatible format call (DeepSeek, OpenAI relay, etc.)"""
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    kwargs = dict(model=MODEL, messages=messages)

    # Enable maximum reasoning effort for DeepSeek models
    if ACTIVE_MODEL == "deepseek":
        kwargs["reasoning_effort"] = "max"
        kwargs["extra_body"] = {"thinking": {"type": "enabled"}}

    response = client.chat.completions.create(**kwargs)

    message = response.choices[0].message
    content = message.content or ""
    reasoning = getattr(message, "reasoning_content", None)

    return content, reasoning


def _call_anthropic(prompt: str) -> tuple[str, str | None]:
    """Native Anthropic format call"""
    client = anthropic.Anthropic(api_key=API_KEY, base_url=BASE_URL)

    response = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )

    # Extract text content
    content = ""
    reasoning = None
    for block in response.content:
        if block.type == "thinking":
            reasoning = block.thinking
        elif block.type == "text":
            content = block.text

    return content, reasoning


def parse_qa_output(raw_output: str) -> list[dict]:
    """Parse the model output into a structured QA list"""
    qa_list = []

    # Split into QA blocks starting with "Q:" (works with or without --- separators)
    # First remove <!-- Part N --> markers
    cleaned = re.sub(r"<!--.*?-->", "", raw_output)
    # Split on lines starting with Q: (keeping the "Q:" itself)
    blocks = re.split(r"(?=^Q:)", cleaned, flags=re.MULTILINE)

    for block in blocks:
        block = block.strip()
        if not block or not block.startswith("Q:"):
            continue

        qa = {}

        # Extract Q
        q_match = re.search(r"^Q:\s*(.+?)(?=\nA:)", block, re.DOTALL)
        if q_match:
            qa["question"] = q_match.group(1).strip()

        # Extract A
        a_match = re.search(r"\nA:\s*(.+?)(?=\nType:)", block, re.DOTALL)
        if a_match:
            qa["answer"] = a_match.group(1).strip()

        # Extract Type
        type_match = re.search(r"Type:\s*(.+?)(?=\n)", block)
        if type_match:
            qa["type"] = type_match.group(1).strip()

        # Extract Evidence
        evidences = re.findall(r"Evidence \d+:\s*(.+?)(?=\n\s*- Evidence|\n\s*$|\nQ:|\Z)", block, re.DOTALL)
        qa["evidences"] = [e.strip() for e in evidences if e.strip()]

        if qa.get("question") and qa.get("answer"):
            qa_list.append(qa)

    return qa_list




ADJACENT_JUDGE_PROMPT = """You are a text analysis expert. Given an original paper text and multiple pairs of evidence passages, determine whether each pair is **adjacent** in the original text.

"Adjacent" means: they are consecutive sentences within the same paragraph, with no substantive content between them (only citation markers, figure references, or whitespace may appear between them).

## Original Paper Text:
{source_text}

## Evidence Pairs to Judge:
{evidence_pairs}

## Task:
For each pair, determine if the two evidences are adjacent in the original text.
Reply with ONLY a JSON array of results, one per pair, in order:
["adjacent", "not_adjacent", "adjacent", ...]
"""


def check_adjacent_evidences(qa_list: list[dict], source_text: str) -> list[dict]:
    """
    Use DeepSeek to batch-judge whether the two evidences of a multi-evidence QA are adjacent.
    If adjacent, downgrade to single-evidence and merge the evidences.
    """
    multi_qas = [qa for qa in qa_list if "multi" in qa.get("type", "") and len(qa.get("evidences", [])) >= 2]

    if not multi_qas:
        print("  No multi-evidence QA, skipping adjacency check.")
        return qa_list

    # Build evidence pairs text
    pairs_text = ""
    for i, qa in enumerate(multi_qas, 1):
        pairs_text += f"### Pair {i}:\n- Evidence 1: {qa['evidences'][0]}\n- Evidence 2: {qa['evidences'][1]}\n\n"

    prompt = ADJACENT_JUDGE_PROMPT.format(
        source_text=source_text,
        evidence_pairs=pairs_text,
    )

    print(f"  Calling DeepSeek to batch-judge adjacency for {len(multi_qas)} evidence pairs...")
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    kwargs = dict(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    if ACTIVE_MODEL == "deepseek":
        kwargs["reasoning_effort"] = "max"
        kwargs["extra_body"] = {"thinking": {"type": "enabled"}}

    response = client.chat.completions.create(**kwargs)
    message = response.choices[0].message
    content = message.content or ""
    reasoning = getattr(message, "reasoning_content", None)

    if reasoning:
        print(f"  [Reasoning process: {len(reasoning)} characters]")

    # Parse results
    results = _parse_adjacent_results(content, reasoning, len(multi_qas))

    # Apply downgrades
    downgraded_count = 0
    for qa, result in zip(multi_qas, results):
        if result == "adjacent":
            ev1 = qa["evidences"][0]
            ev2 = qa["evidences"][1]
            merged_evidence = ev1.rstrip() + " " + ev2.lstrip()
            qa["type"] = "single-evidence"
            qa["evidences"] = [merged_evidence]
            qa["downgraded"] = True
            downgraded_count += 1
            print(f"  [Downgraded] Q: {qa['question'][:60]}... (DeepSeek judged as adjacent)")

    print(f"  Downgraded count: {downgraded_count}/{len(multi_qas)}")
    return qa_list


def _parse_adjacent_results(content: str, reasoning: str | None, expected_count: int) -> list[str]:
    """Parse the adjacency judgment results from the model output"""
    # Try to parse a JSON array from content
    text = content.strip() if content else ""
    if text:
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            try:
                results = json.loads(match.group())
                if len(results) == expected_count:
                    return [r.lower().strip() for r in results]
            except json.JSONDecodeError:
                pass

    # content parsing failed, try extracting from reasoning
    if reasoning:
        match = re.search(r'\[.*\]', reasoning, re.DOTALL)
        if match:
            try:
                results = json.loads(match.group())
                if len(results) == expected_count:
                    return [r.lower().strip() for r in results]
            except json.JSONDecodeError:
                pass

    # Both failed, return unknown (no downgrade)
    print(f"  [Warning] Failed to parse adjacency judgment results, skipping downgrade. content: {text[:200]}")
    return ["not_adjacent"] * expected_count


# ============ Step 2: Necessity check ============

NECESSITY_JUDGE_PROMPT = """You are a QA quality evaluator. For each question-answer-evidence triplet below, determine whether **both** evidence passages are necessary to answer the question, or if one alone is sufficient.

"Necessary" means: removing either evidence would make it impossible to fully answer the question. The question requires information from BOTH passages.
"Redundant" means: one evidence alone already contains enough information to answer the question completely.

## Evidence Triplets to Judge:
{triplets}

## Task:
For each triplet, reply with a JSON object: {{"verdict": "necessary"}} or {{"verdict": "redundant", "keep": 1}} (or "keep": 2).
- "keep" indicates which evidence alone is sufficient.

Reply with ONLY a JSON array of results, one per triplet, in order:
[{{"verdict": "necessary"}}, {{"verdict": "redundant", "keep": 1}}, ...]
"""


def check_evidence_necessity(qa_list: list[dict]) -> list[dict]:
    """
    For QA still marked as multi-evidence, judge whether both evidences are necessary.
    If redundant, downgrade to single-evidence and keep only the necessary evidence.
    """
    multi_qas = [qa for qa in qa_list if "multi" in qa.get("type", "") and len(qa.get("evidences", [])) >= 2]

    if not multi_qas:
        print("  No multi-evidence QA, skipping necessity check.")
        return qa_list

    # Build triplets text
    triplets_text = ""
    for i, qa in enumerate(multi_qas, 1):
        triplets_text += (
            f"### Triplet {i}:\n"
            f"- Question: {qa['question']}\n"
            f"- Answer: {qa['answer']}\n"
            f"- Evidence 1: {qa['evidences'][0]}\n"
            f"- Evidence 2: {qa['evidences'][1]}\n\n"
        )

    prompt = NECESSITY_JUDGE_PROMPT.format(triplets=triplets_text)

    print(f"  Calling DeepSeek to batch-judge necessity for {len(multi_qas)} evidence pairs...")
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    kwargs = dict(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    if ACTIVE_MODEL == "deepseek":
        kwargs["reasoning_effort"] = "max"
        kwargs["extra_body"] = {"thinking": {"type": "enabled"}}

    response = client.chat.completions.create(**kwargs)
    message = response.choices[0].message
    content = message.content or ""
    reasoning = getattr(message, "reasoning_content", None)

    if reasoning:
        print(f"  [Reasoning process: {len(reasoning)} characters]")

    # Parse results
    results = _parse_necessity_results(content, reasoning, len(multi_qas))

    # Apply downgrades
    downgraded_count = 0
    for qa, result in zip(multi_qas, results):
        if result["verdict"] == "redundant":
            keep_idx = result.get("keep", 1) - 1  # convert to 0-based
            keep_idx = max(0, min(1, keep_idx))  # ensure within 0-1 range
            qa["type"] = "single-evidence"
            qa["evidences"] = [qa["evidences"][keep_idx]]
            qa["downgraded"] = True
            downgraded_count += 1
            print(f"  [Downgraded] Q: {qa['question'][:60]}... (redundant, keeping Evidence {keep_idx + 1})")

    print(f"  Downgraded due to redundancy: {downgraded_count}/{len(multi_qas)}")
    return qa_list


def _parse_necessity_results(content: str, reasoning: str | None, expected_count: int) -> list[dict]:
    """Parse the necessity judgment results from the model output"""
    text = content.strip() if content else ""

    for source in [text, reasoning or ""]:
        if not source:
            continue
        match = re.search(r'\[.*\]', source, re.DOTALL)
        if match:
            try:
                results = json.loads(match.group())
                if len(results) == expected_count:
                    # Normalize result format
                    normalized = []
                    for r in results:
                        if isinstance(r, dict):
                            normalized.append({"verdict": r.get("verdict", "necessary").lower(), "keep": r.get("keep", 1)})
                        elif isinstance(r, str):
                            normalized.append({"verdict": r.lower().strip(), "keep": 1})
                        else:
                            normalized.append({"verdict": "necessary", "keep": 1})
                    return normalized
            except json.JSONDecodeError:
                pass

    # Both failed, default to keeping (no downgrade)
    print(f"  [Warning] Failed to parse necessity judgment results, skipping downgrade. content: {text[:200]}")
    return [{"verdict": "necessary", "keep": 1}] * expected_count


def save_results(qa_list: list[dict], raw_output: str, doc_name: str):
    """Save results"""
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Save raw output as md (the LLM output is already in markdown format)
    raw_path = OUTPUT_DIR / f"{doc_name}_raw.md"
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(raw_output)
    print(f"Raw output saved: {raw_path}")

    # Save structured JSON
    json_path = OUTPUT_DIR / f"{doc_name}_qa.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(qa_list, f, ensure_ascii=False, indent=2)
    print(f"Structured QA saved: {json_path}")


def process_single_doc(doc_path: Path, species: str = "mouse") -> list[dict]:
    """Process a single document, return a list of QA"""
    doc_name = doc_path.stem[:50]
    print(f"\n{'=' * 60}")
    print(f"Document: {doc_path.name}")
    print(f"File size: {doc_path.stat().st_size / 1024:.1f} KB")

    # Read the document
    paper_content = load_document(doc_path)
    paper_content = strip_references(paper_content)
    print(f"After removing References: {len(paper_content)} characters ({len(paper_content.encode('utf-8')) / 1024:.1f} KB)")

    # Dynamic splitting: max 4 parts for mouse, unlimited for macaque
    max_parts = 4 if species == "mouse" else 99
    parts = split_document(paper_content, max_parts=max_parts)
    num_parts = len(parts)
    print(f"Number of parts: {num_parts}")
    if num_parts > 1:
        for i, part in enumerate(parts, 1):
            print(f"  Part {i}: {len(part)} characters")

    # Generate 10 single + 8 multi per part
    single_per_part = 10
    multi_per_part = 8

    # Call the API part by part
    all_qa = []
    all_raw = []

    for i, part in enumerate(parts, 1):
        if num_parts > 1:
            print(f"\n--- Part {i}/{num_parts} ---")

        raw_output = call_llm(part, f"{doc_name}_part{i}", single_per_part, multi_per_part)
        print(f"Model output length: {len(raw_output)} characters")

        qa_list = parse_qa_output(raw_output)
        print(f"Parsed {len(qa_list)} QA pairs")

        all_qa.extend(qa_list)
        all_raw.append(raw_output)

    # Merge raw outputs
    combined_raw = "\n\n---\n\n".join(
        f"<!-- Part {i} -->\n\n{raw}" for i, raw in enumerate(all_raw, 1)
    ) if num_parts > 1 else all_raw[0]

    # Check multi-evidence adjacency, downgrade violating entries
    print("\nChecking multi-evidence adjacency...")
    all_qa = check_adjacent_evidences(all_qa, paper_content)

    # Check multi-evidence necessity, downgrade redundant entries
    print("Checking multi-evidence necessity...")
    all_qa = check_evidence_necessity(all_qa)

    # Statistics
    single_count = sum(1 for qa in all_qa if "single" in qa.get("type", ""))
    multi_count = sum(1 for qa in all_qa if "multi" in qa.get("type", ""))
    print(f"Result: {len(all_qa)} QA (single: {single_count}, multi: {multi_count})")

    # Save single-document result
    save_results(all_qa, combined_raw, doc_name)

    return all_qa


def get_completed_docs() -> set[str]:
    """Check the output directory for already-completed documents (resume support)"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    completed = set()
    for f in OUTPUT_DIR.glob("*_qa.json"):
        # Filename format: <doc_stem>_qa.json
        stem = f.stem.replace("_qa", "")
        completed.add(stem)
    return completed


def merge_all_qa(species: str = "all"):
    """Merge per-document QA JSON files into files split by species"""
    OUTPUT_DIR.mkdir(exist_ok=True)

    mouse_qa = []
    macaque_qa = []

    # Get filename prefixes for mouse and macaque
    mouse_stems = {f.stem[:50] for f in MOUSE_DOC_DIR.glob("*.md")}
    macaque_stems = {f.stem[:50] for f in MACAQUE_DOC_DIR.glob("*.md")}

    for f in sorted(OUTPUT_DIR.glob("*_qa.json")):
        if "merged" in f.name:
            continue
        qa_data = json.loads(f.read_text(encoding="utf-8"))
        stem = f.stem.replace("_qa", "")

        if stem in mouse_stems:
            mouse_qa.extend(qa_data)
        elif stem in macaque_stems:
            macaque_qa.extend(qa_data)
        else:
            # Try fuzzy matching
            if any(stem.startswith(ms[:20]) for ms in mouse_stems):
                mouse_qa.extend(qa_data)
            elif any(stem.startswith(ms[:20]) for ms in macaque_stems):
                macaque_qa.extend(qa_data)
            else:
                mouse_qa.extend(qa_data)  # fallback

    # Save by species
    if mouse_qa and species in ("mouse", "all"):
        path = OUTPUT_DIR / "all_qa_mouse.json"
        path.write_text(json.dumps(mouse_qa, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Mouse QA merged: {path} ({len(mouse_qa)} pairs)")

    if macaque_qa and species in ("macaque", "all"):
        path = OUTPUT_DIR / "all_qa_macaque.json"
        path.write_text(json.dumps(macaque_qa, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Macaque QA merged: {path} ({len(macaque_qa)} pairs)")

    total = len(mouse_qa) + len(macaque_qa)
    print(f"Total: {total} QA pairs")


def main():
    """Batch process all documents, with resume support"""
    import argparse
    parser = argparse.ArgumentParser(description="Generate QA pairs from papers")
    parser.add_argument("--species", choices=["mouse", "macaque", "all"], default="all",
                        help="Species to process (default: all)")
    parser.add_argument("--merge-only", action="store_true",
                        help="Only merge existing outputs without generating")
    args = parser.parse_args()

    print(f"Model: {MODEL} ({BASE_URL})")
    print()

    if args.merge_only:
        merge_all_qa(args.species)
        return

    # Collect documents (doc_path, species)
    doc_files = []
    if args.species in ("mouse", "all"):
        doc_files.extend((f, "mouse") for f in sorted(MOUSE_DOC_DIR.glob("*.md")))
    if args.species in ("macaque", "all"):
        doc_files.extend((f, "macaque") for f in sorted(MACAQUE_DOC_DIR.glob("*.md")))

    if not doc_files:
        print("No markdown documents found!")
        return

    # Resume support: check already-completed documents
    completed = get_completed_docs()
    pending = []
    for doc, species in doc_files:
        stem = doc.stem[:50]
        if stem in completed:
            print(f"[Skipped] {doc.name} (already completed)")
        else:
            pending.append((doc, species))

    print(f"\nTotal documents: {len(doc_files)}, completed: {len(completed)}, pending: {len(pending)}")

    if not pending:
        print("All documents have been processed.")
        merge_all_qa(args.species)
        return

    # Process documents one by one
    for idx, (doc_path, species) in enumerate(pending, 1):
        print(f"\n[{idx}/{len(pending)}] Processing...")
        try:
            process_single_doc(doc_path, species=species)
        except Exception as e:
            print(f"[Error] {doc_path.name}: {e}")
            print("Skipping this document, continuing to the next...")
            continue

    # Merge after all are done
    merge_all_qa(args.species)


if __name__ == "__main__":
    main()
