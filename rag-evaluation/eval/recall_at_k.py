"""
Recall@10 Multi-Model Voting Evaluation

3 models (GPT-5.4, Claude Sonnet 4, Gemini 3.1 Pro) evaluate in parallel.
Only applicable to RAG results (needs retrieved chunks to evaluate).

Uses RAGAS Context Recall methodology: for each ground truth evidence,
LLM judges whether the top-K retrieved chunks contain its core information.

Usage:
  python eval/recall_at_k.py --species mouse
  python eval/recall_at_k.py --species macaque
  python eval/recall_at_k.py --vote
"""

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from statistics import mode as stats_mode

from dotenv import load_dotenv
from openai import OpenAI

# Load .env from project root
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env")

# --- Model configs ---
MODELS = {
    "gpt": {
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "base_url": os.getenv("OPENAI_BASE_URL", ""),
        "model": os.getenv("OPENAI_MODEL", ""),
    },
    "claude": {
        "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
        "base_url": os.getenv("ANTHROPIC_BASE_URL", ""),
        "model": os.getenv("ANTHROPIC_MODEL", ""),
    },
    "gemini": {
        "api_key": os.getenv("GEMINI_API_KEY", ""),
        "base_url": os.getenv("GEMINI_BASE_URL", ""),
        "model": os.getenv("GEMINI_MODEL", ""),
    },
}

TOP_K = 10

# --- Recall judge prompt (embedded) ---
RECALL_PROMPT = """\
You are evaluating a retrieval system. Given a ground truth evidence statement and a set of retrieved text chunks, determine whether the retrieved chunks contain the key information from the evidence.

## Ground Truth Evidence:
{evidence}

## Retrieved Chunks (top-{top_k}):
{chunks}

## Task:
Does ANY of the retrieved chunks contain the core information stated in the ground truth evidence? Minor differences in formatting (e.g., LaTeX symbols vs plain text, citation markers) should be ignored -- focus on whether the factual content is present.

Reply with ONLY a JSON object:
{{"attributed": true, "reason": "<brief>"}} or {{"attributed": false, "reason": "<brief>"}}
"""

# --- Results directory ---
RECALL_DIR = ROOT_DIR / "results" / "recall"


# ============================================================
# Core recall judge logic
# ============================================================

def judge_single_evidence(client: OpenAI, model_name: str,
                          evidence: str, chunks: list[str]) -> dict:
    """Judge whether a single evidence is covered by retrieved chunks.
    Returns {"attributed": bool, "reason": str}."""
    chunks_text = ""
    for i, chunk in enumerate(chunks, 1):
        chunks_text += f"### Chunk {i}:\n{chunk}\n\n"

    prompt = RECALL_PROMPT.format(
        evidence=evidence,
        chunks=chunks_text,
        top_k=TOP_K,
    )

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        content = response.choices[0].message.content or ""
        if not content.strip():
            reasoning = getattr(response.choices[0].message, "reasoning_content", None)
            if reasoning:
                content = reasoning

        # Try full JSON parse
        json_match = re.search(r'\{[^}]*"attributed"[^}]*\}', content, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
                return {
                    "attributed": bool(result.get("attributed", False)),
                    "reason": result.get("reason", ""),
                }
            except json.JSONDecodeError:
                pass

        # Fallback
        match = re.search(r'"attributed"\s*:\s*(true|false)', content, re.IGNORECASE)
        attributed = match.group(1).lower() == "true" if match else "true" in content.lower()
        return {"attributed": attributed, "reason": "parse fallback"}
    except Exception as e:
        print(f"    API error: {e}")
        return {"attributed": False, "reason": f"API error: {e}"}


# ============================================================
# Data loading
# ============================================================

def load_data(species: str) -> list[dict]:
    """
    Load retrieval results + ground truth evidences.
    Returns list of {"question", "type", "evidences", "retrieved_docs"}.
    """
    qa_file = ROOT_DIR / "output" / f"all_qa_{species}.json"
    if not qa_file.exists():
        print(f"Error: {qa_file} not found")
        sys.exit(1)
    qa_data = json.loads(qa_file.read_text(encoding="utf-8"))
    qa_map = {qa["question"]: qa for qa in qa_data}

    rag_file = ROOT_DIR / "results" / f"get_retrieved_chunks_output_{species}_top10.json"
    if not rag_file.exists():
        print(f"Error: {rag_file} not found")
        sys.exit(1)
    rag_data = json.loads(rag_file.read_text(encoding="utf-8"))

    items = []
    for entry in rag_data:
        question = entry["question"]
        qa = qa_map.get(question)
        if not qa:
            continue
        items.append({
            "question": question,
            "type": qa["type"],
            "evidences": qa["evidences"],
            "retrieved_docs": entry["retrieved_docs"],
        })
    return items


# ============================================================
# Single-model evaluation with checkpoint
# ============================================================

def run_single_model(model_short: str, items: list[dict], species: str):
    """Run recall evaluation for one model, with checkpoint resume."""
    RECALL_DIR.mkdir(parents=True, exist_ok=True)
    out_file = RECALL_DIR / f"recall_{species}_{model_short}.json"

    # Load existing results for resume
    existing = []
    if out_file.exists():
        existing = json.loads(out_file.read_text(encoding="utf-8"))
    done_count = len(existing)

    if done_count >= len(items):
        print(f"  [{model_short}] Already complete ({done_count}/{len(items)}), skipping.")
        return

    if done_count > 0:
        print(f"  [{model_short}] Resuming from {done_count}/{len(items)}")

    cfg = MODELS[model_short]
    client = OpenAI(api_key=cfg["api_key"], base_url=cfg["base_url"])
    model_name = cfg["model"]

    results = list(existing)
    for i in range(done_count, len(items)):
        item = items[i]
        evidences = item["evidences"]
        retrieved_docs = item["retrieved_docs"]

        # Judge each evidence
        hits = 0
        evidence_results = []
        for ev in evidences:
            judgment = judge_single_evidence(client, model_name, ev, retrieved_docs)
            evidence_results.append({
                "attributed": judgment["attributed"],
                "reason": judgment["reason"],
            })
            if judgment["attributed"]:
                hits += 1

        recall = hits / len(evidences) if evidences else 0.0

        results.append({
            "question": item["question"],
            "type": item["type"],
            "n_evidences": len(evidences),
            "hits": hits,
            "recall": recall,
            "evidence_results": evidence_results,
        })
        # Checkpoint save
        out_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  [{model_short}] {i+1}/{len(items)} recall={recall:.2f} ({hits}/{len(evidences)})")

    print(f"  [{model_short}] Done. Saved to {out_file.name}")


# ============================================================
# Parallel evaluation (3 models)
# ============================================================

def run_evaluate(species: str):
    """Run all 3 models in parallel for a given species."""
    items = load_data(species)
    print(f"Loaded {len(items)} items for {species}")
    model_list = ", ".join(f"{k}={v['model']}" for k, v in MODELS.items())
    print(f"Models: {model_list}")
    print(f"Top-K: {TOP_K}")
    print("=" * 60)

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(run_single_model, model_short, items, species): model_short
            for model_short in MODELS
        }
        for future in as_completed(futures):
            model_short = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"  [{model_short}] FAILED: {e}")

    print(f"\nAll models done for {species}.")


# ============================================================
# Voting
# ============================================================

def vote_recall(values: list[float]):
    """
    Majority vote for recall. Returns None on 3-way split (conflict).
    """
    valid = [v for v in values if v is not None]
    if not valid:
        return None
    try:
        return stats_mode(valid)
    except Exception:
        # No unique mode — conflict
        return None


def run_vote():
    """Read all per-model recall files, produce voted results and summary."""
    RECALL_DIR.mkdir(parents=True, exist_ok=True)

    # Discover species from existing files
    species_set = set()
    for f in RECALL_DIR.glob("recall_*_*.json"):
        parts = f.stem.split("_")
        # recall_{species}_{model}
        if len(parts) >= 3 and parts[-1] in ("gpt", "claude", "gemini"):
            species_set.add(parts[1])

    if not species_set:
        print("No recall result files found in results/recall/")
        return

    summary_lines = []
    all_voted_items = []  # for aggregate
    all_resolved_maps = []  # track resolved conflicts per species offset

    for species in sorted(species_set):
        print(f"\n{'='*60}")
        print(f"Voting: {species}")
        print(f"{'='*60}")

        # Load per-model results
        model_results = {}
        for model_short in MODELS:
            f = RECALL_DIR / f"recall_{species}_{model_short}.json"
            if f.exists():
                model_results[model_short] = json.loads(f.read_text(encoding="utf-8"))
            else:
                print(f"  Warning: {f.name} not found, skipping this model")

        if len(model_results) < 2:
            print(f"  Need at least 2 model results to vote, skipping.")
            continue

        n_items = min(len(v) for v in model_results.values())
        print(f"  Items: {n_items}, Models: {list(model_results.keys())}")

        voted = []
        conflicts = []

        for i in range(n_items):
            recall_values = []
            question = None
            qa_type = None
            model_recalls = {}

            for model_short, results in model_results.items():
                entry = results[i]
                if question is None:
                    question = entry["question"]
                    qa_type = entry.get("type", "")
                recall_values.append(entry["recall"])
                model_recalls[model_short] = entry["recall"]

            voted_recall = vote_recall(recall_values)
            voted.append({
                "question": question,
                "type": qa_type,
                "recall": voted_recall,
                "model_recalls": model_recalls,
            })

            if voted_recall is None:
                conflicts.append({
                    "index": i,
                    "question": question,
                    "type": qa_type,
                    "model_recalls": model_recalls,
                    "resolved_recall": None,
                })

        # Save voted results
        voted_file = RECALL_DIR / f"recall_{species}_voted.json"
        voted_file.write_text(json.dumps(voted, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  Saved: {voted_file.name}")

        # Save conflicts
        conflicts_file = RECALL_DIR / f"recall_{species}_conflicts.json"
        if conflicts:
            conflicts_file.write_text(json.dumps(conflicts, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"  Conflicts: {len(conflicts)} items -> {conflicts_file.name}")
        elif conflicts_file.exists():
            conflicts_file.unlink()

        # Read resolved conflicts
        resolved_map = {}
        if conflicts_file.exists():
            cf_data = json.loads(conflicts_file.read_text(encoding="utf-8"))
            for cf in cf_data:
                if cf.get("resolved_recall") is not None:
                    resolved_map[cf["index"]] = cf["resolved_recall"]

        # Track for aggregate
        offset = len(all_voted_items)
        all_voted_items.extend(voted)
        all_resolved_maps.append((offset, resolved_map))

        # Per-species summary
        summary_lines.append(f"\n{'='*60}")
        summary_lines.append(f"{species}")
        summary_lines.append(f"{'='*60}")
        summary_lines.append(f"Total items: {n_items}")
        summary_lines.append(f"Models: {', '.join(model_results.keys())}")

        valid_r = []
        unresolved = 0
        for i, v in enumerate(voted):
            r = v["recall"]
            if r is None:
                if i in resolved_map:
                    valid_r.append(resolved_map[i])
                else:
                    unresolved += 1
            else:
                valid_r.append(r)

        if valid_r:
            summary_lines.append(f"Avg Recall@{TOP_K}: {sum(valid_r)/len(valid_r):.3f}")

        if conflicts:
            n_resolved = len(resolved_map)
            summary_lines.append(f"Conflicts: {len(conflicts)} total, {n_resolved} resolved, {unresolved} pending review")

        for qa_type_label in ("single-evidence", "multi-evidence"):
            sub = []
            for i, v in enumerate(voted):
                if v.get("type") != qa_type_label:
                    continue
                r = v["recall"]
                if r is None and i in resolved_map:
                    r = resolved_map[i]
                if r is not None:
                    sub.append(r)
            if sub:
                avg = sum(sub) / len(sub)
                summary_lines.append(f"  {qa_type_label} ({len(sub)}): recall={avg:.3f}")

    # --- Pivot table ---
    # Collect voted data by species (with resolved conflicts applied)
    voted_by_species = {}
    for species in sorted(species_set):
        voted_file = RECALL_DIR / f"recall_{species}_voted.json"
        if not voted_file.exists():
            continue
        data = json.loads(voted_file.read_text(encoding="utf-8"))

        cf_file = RECALL_DIR / f"recall_{species}_conflicts.json"
        if cf_file.exists():
            cf_data = json.loads(cf_file.read_text(encoding="utf-8"))
            for cf in cf_data:
                if cf.get("resolved_recall") is not None:
                    data[cf["index"]]["recall"] = cf["resolved_recall"]

        voted_by_species[species] = data

    def calc_recall_metrics(items):
        """Calculate (n, avg_recall) for a list of voted items."""
        r_vals = [v["recall"] for v in items if v["recall"] is not None]
        n = len(items)
        avg_r = sum(r_vals) / len(r_vals) if r_vals else None
        return n, avg_r

    # Build pivot rows
    rows = []
    for species in sorted(voted_by_species.keys()):
        data = voted_by_species[species]
        for type_label in ("single-evidence", "multi-evidence"):
            sub = [v for v in data if v.get("type") == type_label]
            rows.append((f"{species} / {type_label}", sub))
        rows.append((f"{species} / ALL", data))

    all_items = [v for data in voted_by_species.values() for v in data]
    for type_label in ("single-evidence", "multi-evidence"):
        sub = [v for v in all_items if v.get("type") == type_label]
        rows.append((f"All species / {type_label}", sub))
    rows.append(("ALL", all_items))

    # Format table
    col_w = 30
    summary_lines.append(f"\n{'='*60}")
    summary_lines.append("PIVOT TABLE (Recall@10, RAG only)")
    summary_lines.append(f"{'='*60}")

    header = f"{'':>{col_w}} | {'Items':>5} {'Recall':>7}"
    sep = f"{'-'*col_w}-+-{'-'*14}"
    summary_lines.append(header)
    summary_lines.append(sep)

    for label, items in rows:
        n, avg_r = calc_recall_metrics(items)
        avg_str = f"{avg_r:.3f}" if avg_r is not None else "  -  "
        summary_lines.append(f"{label:>{col_w}} | {n:>5} {avg_str:>7}")

    # Save summary
    summary_text = "\n".join(summary_lines)
    summary_file = RECALL_DIR / "recall_summary.txt"
    summary_file.write_text(summary_text, encoding="utf-8")
    print(f"\n{'='*60}")
    print(summary_text)
    print(f"\nSummary saved to: {summary_file}")


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Multi-model voting Recall@10 evaluation (RAG only)"
    )
    parser.add_argument("--species", choices=["mouse", "macaque"],
                        help="Species to evaluate")
    parser.add_argument("--vote", action="store_true",
                        help="Run majority voting on existing per-model results")
    args = parser.parse_args()

    if args.vote:
        run_vote()
    elif args.species:
        run_evaluate(args.species)
    else:
        parser.error("Either --vote or --species is required.")


if __name__ == "__main__":
    main()
