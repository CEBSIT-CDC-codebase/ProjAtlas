"""
Correctness + Hallucination Multi-Model Voting Judge

3 models (GPT-5.4, Claude Sonnet 4, Gemini 3.1 Pro) evaluate in parallel.
Supports resume from checkpoint and majority voting.

Usage:
  python eval/judge_correctness.py --species mouse --mode rag
  python eval/judge_correctness.py --species mouse --mode norag
  python eval/judge_correctness.py --species macaque --mode rag
  python eval/judge_correctness.py --species macaque --mode norag
  python eval/judge_correctness.py --vote
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

# --- Judge prompt (embedded) ---
JUDGE_PROMPT = """\
You are an expert evaluator for a language model answering domain-specific questions.
You will be given a Question, a Ground Truth Answer, and the Model's Response.
Evaluate the response on two dimensions.

## Evaluation Criteria

### 1. Correctness (0 / 0.5 / 1)
- 1: The response is factually accurate and complete relative to the ground truth.
- 0.5: Partially correct — captures the main point but misses key details or has minor inaccuracies.
- 0: Incorrect or fails to answer the question.

### 2. Hallucination (0 / 1)
- 0: No fabricated information. Either states correct facts, gives a vague response, or admits uncertainty.
- 1: Presents specific claims that contradict the ground truth or are clearly fabricated (invented references, statistics, or false specifics stated with confidence).

## Input
**Question:** {question}
**Ground Truth Answer:** {ground_truth}
**Model Response:** {model_response}

## Output Format
Return ONLY a JSON object:
{{"correctness": <0 | 0.5 | 1>, "correctness_reason": "<brief>", "hallucination": <0 | 1>, "hallucination_reason": "<brief>"}}
"""

# --- Results directory ---
JUDGE_DIR = ROOT_DIR / "results" / "judge"


# ============================================================
# Core judge logic
# ============================================================

def parse_judge_output(content: str) -> dict:
    """Extract correctness/hallucination from LLM response."""
    # Try full JSON extraction
    json_match = re.search(r'\{[^}]*"correctness"[^}]*\}', content, re.DOTALL)
    if json_match:
        try:
            result = json.loads(json_match.group())
            return result
        except json.JSONDecodeError:
            pass

    # Fallback: regex per field
    correctness_match = re.search(r'"correctness"\s*:\s*([\d.]+)', content)
    hallucination_match = re.search(r'"hallucination"\s*:\s*(\d)', content)
    return {
        "correctness": float(correctness_match.group(1)) if correctness_match else None,
        "correctness_reason": "parse fallback",
        "hallucination": int(hallucination_match.group(1)) if hallucination_match else None,
        "hallucination_reason": "parse fallback",
    }


def judge_single(client: OpenAI, model_name: str, question: str,
                 ground_truth: str, model_response: str) -> dict:
    """Call one judge model for a single QA pair."""
    prompt = (JUDGE_PROMPT
              .replace("{question}", question)
              .replace("{ground_truth}", ground_truth)
              .replace("{model_response}", model_response))

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        content = response.choices[0].message.content or ""
        # Some models put result in reasoning_content
        if not content.strip():
            reasoning = getattr(response.choices[0].message, "reasoning_content", None)
            if reasoning:
                content = reasoning
        return parse_judge_output(content)
    except Exception as e:
        return {
            "correctness": None,
            "correctness_reason": f"API error: {e}",
            "hallucination": None,
            "hallucination_reason": f"API error: {e}",
        }


# ============================================================
# Data loading
# ============================================================

def load_data(species: str, mode: str) -> list[dict]:
    """
    Load QA pairs with model responses and ground truth.
    Returns list of {"question", "ground_truth", "model_response", "type"}.
    """
    # Ground truth
    qa_file = ROOT_DIR / "output" / f"all_qa_{species}.json"
    if not qa_file.exists():
        print(f"Error: {qa_file} not found")
        sys.exit(1)
    qa_data = json.loads(qa_file.read_text(encoding="utf-8"))
    qa_map = {qa["question"]: qa for qa in qa_data}

    # Model responses
    MODE_FILES = {
        "rag": ROOT_DIR / "results" / f"get_retrieved_chunks_output_{species}_top10.json",
        "without_rag_mistral": ROOT_DIR / "results" / f"without_rag_{species}_mistral.json",
        "without_rag_deepseek": ROOT_DIR / "results" / f"without_rag_{species}_deepseek.json",
        "without_rag_qwen2.5": ROOT_DIR / "results" / f"without_rag_{species}_qwen2.5.json",
        "without_rag_llama3.3": ROOT_DIR / "results" / f"without_rag_{species}_llama3.3.json",
    }
    if mode not in MODE_FILES:
        print(f"Error: unknown mode '{mode}'")
        sys.exit(1)
    resp_file = MODE_FILES[mode]

    if not resp_file.exists():
        print(f"Error: {resp_file} not found")
        sys.exit(1)
    resp_data = json.loads(resp_file.read_text(encoding="utf-8"))

    # Merge
    items = []
    for entry in resp_data:
        question = entry["question"]
        qa = qa_map.get(question)
        if not qa:
            continue
        items.append({
            "question": question,
            "ground_truth": qa["answer"],
            "model_response": entry["answer"],
            "type": qa["type"],
        })
    return items


# ============================================================
# Single-model evaluation with checkpoint
# ============================================================

def run_single_model(model_short: str, items: list[dict], species: str, mode: str):
    """Run evaluation for one model, with checkpoint resume."""
    JUDGE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = JUDGE_DIR / f"judge_{species}_{mode}_{model_short}.json"

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
        judgment = judge_single(
            client, model_name,
            item["question"], item["ground_truth"], item["model_response"]
        )
        results.append({
            "question": item["question"],
            "type": item["type"],
            "correctness": judgment.get("correctness"),
            "correctness_reason": judgment.get("correctness_reason", ""),
            "hallucination": judgment.get("hallucination"),
            "hallucination_reason": judgment.get("hallucination_reason", ""),
        })
        # Save after each item (checkpoint)
        out_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

        status = f"c={judgment.get('correctness')} h={judgment.get('hallucination')}"
        print(f"  [{model_short}] {i+1}/{len(items)} {status}")

    print(f"  [{model_short}] Done. Saved to {out_file.name}")


# ============================================================
# Parallel evaluation (3 models)
# ============================================================

def run_evaluate(species: str, mode: str):
    """Run all 3 models in parallel for a given species+mode."""
    items = load_data(species, mode)
    print(f"Loaded {len(items)} items for {species}/{mode}")
    model_list = ", ".join(f"{k}={v['model']}" for k, v in MODELS.items())
    print(f"Models: {model_list}")
    print("=" * 60)

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(run_single_model, model_short, items, species, mode): model_short
            for model_short in MODELS
        }
        for future in as_completed(futures):
            model_short = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"  [{model_short}] FAILED: {e}")

    print(f"\nAll models done for {species}/{mode}.")


# ============================================================
# Voting
# ============================================================

def vote_correctness(values: list):
    """Majority vote for correctness (0, 0.5, 1). Returns None on 3-way split."""
    valid = [v for v in values if v is not None]
    if len(valid) < 2:
        return None
    try:
        return stats_mode(valid)
    except Exception:
        # 3-way split (all different)
        return None


def vote_hallucination(values: list):
    """Majority vote for hallucination (0 or 1)."""
    valid = [v for v in values if v is not None]
    if len(valid) < 2:
        return None
    return stats_mode(valid)


def run_vote():
    """Read all per-model judge files, produce voted results and summary."""
    JUDGE_DIR.mkdir(parents=True, exist_ok=True)

    # Discover all (species, mode) combos from existing files
    KNOWN_MODES = ["rag", "without_rag_mistral", "without_rag_deepseek", "without_rag_qwen2.5", "without_rag_llama3.3"]
    combos = set()
    for f in JUDGE_DIR.glob("judge_*_*_*.json"):
        name = f.stem  # e.g. judge_mouse_rag_gpt
        for model_short in ("gpt", "claude", "gemini"):
            suffix = f"_{model_short}"
            if name.endswith(suffix):
                middle = name[len("judge_"):-len(suffix)]
                # middle is e.g. "mouse_rag" or "mouse_without_rag_qwen2.5"
                for known_mode in sorted(KNOWN_MODES, key=len, reverse=True):
                    if middle.endswith(f"_{known_mode}"):
                        species = middle[: -(len(known_mode) + 1)]
                        combos.add((species, known_mode))
                        break
                break

    if not combos:
        print("No judge result files found in results/judge/")
        return

    summary_lines = []

    # Sort: rag first, then without_rag variants; within each mode, alphabetical species
    mode_order = {"rag": 0, "without_rag_mistral": 1, "without_rag_deepseek": 2, "without_rag_qwen2.5": 3, "without_rag_llama3.3": 4}
    sorted_combos = sorted(combos, key=lambda x: (mode_order.get(x[1], 9), x[0]))

    for species, mode in sorted_combos:
        print(f"\n{'='*60}")
        print(f"Voting: {species} / {mode}")
        print(f"{'='*60}")

        # Load per-model results
        model_results = {}
        for model_short in MODELS:
            f = JUDGE_DIR / f"judge_{species}_{mode}_{model_short}.json"
            if f.exists():
                model_results[model_short] = json.loads(f.read_text(encoding="utf-8"))
            else:
                print(f"  Warning: {f.name} not found, skipping this model")

        if len(model_results) < 2:
            print(f"  Need at least 2 model results to vote, skipping.")
            continue

        # Determine item count (use shortest)
        n_items = min(len(v) for v in model_results.values())
        print(f"  Items: {n_items}, Models: {list(model_results.keys())}")

        voted = []
        conflicts = []

        for i in range(n_items):
            # Gather scores from each model
            c_values = []
            h_values = []
            reasons = {}
            question = None
            qa_type = None

            for model_short, results in model_results.items():
                entry = results[i]
                if question is None:
                    question = entry["question"]
                    qa_type = entry.get("type", "")
                c_values.append(entry.get("correctness"))
                h_values.append(entry.get("hallucination"))
                reasons[model_short] = {
                    "correctness": entry.get("correctness"),
                    "correctness_reason": entry.get("correctness_reason", ""),
                    "hallucination": entry.get("hallucination"),
                    "hallucination_reason": entry.get("hallucination_reason", ""),
                }

            voted_c = vote_correctness(c_values)
            voted_h = vote_hallucination(h_values)

            item = {
                "question": question,
                "type": qa_type,
                "correctness": voted_c,
                "hallucination": voted_h,
                "model_scores": reasons,
            }
            voted.append(item)

            if voted_c is None:
                conflicts.append({
                    "index": i,
                    "question": question,
                    "type": qa_type,
                    "model_scores": reasons,
                    "resolved_correctness": None,
                })

        # Save voted results
        voted_file = JUDGE_DIR / f"judge_{species}_{mode}_voted.json"
        voted_file.write_text(json.dumps(voted, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  Saved: {voted_file.name}")

        # Save conflicts
        conflicts_file = JUDGE_DIR / f"judge_{species}_{mode}_conflicts.json"
        if conflicts:
            conflicts_file.write_text(json.dumps(conflicts, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"  Conflicts: {len(conflicts)} items -> {conflicts_file.name}")
        elif conflicts_file.exists():
            conflicts_file.unlink()

        # Compute summary
        mode_label = mode.upper().replace("_", " ")
        summary_lines.append(f"\n{'='*60}")
        summary_lines.append(f"{mode_label} / {species}")
        summary_lines.append(f"{'='*60}")
        summary_lines.append(f"Total items: {n_items}")
        summary_lines.append(f"Models: {', '.join(model_results.keys())}")

        # Read resolved conflicts if available
        resolved_map = {}
        if conflicts_file.exists():
            cf_data = json.loads(conflicts_file.read_text(encoding="utf-8"))
            for cf in cf_data:
                if cf.get("resolved_correctness") is not None:
                    resolved_map[cf["index"]] = cf["resolved_correctness"]

        # Compute metrics
        valid_c = []
        unresolved = 0
        for i, v in enumerate(voted):
            c = v["correctness"]
            if c is None:
                if i in resolved_map:
                    valid_c.append(resolved_map[i])
                else:
                    unresolved += 1
            else:
                valid_c.append(c)

        valid_h = [v["hallucination"] for v in voted if v["hallucination"] is not None]

        if valid_c:
            avg_c = sum(valid_c) / len(valid_c)
            summary_lines.append(f"Avg Correctness: {avg_c:.1%} ({len(valid_c)} scored)")
        if valid_h:
            h_rate = sum(1 for h in valid_h if h == 1) / len(valid_h)
            summary_lines.append(f"Hallucination Rate: {h_rate:.1%} ({sum(1 for h in valid_h if h == 1)}/{len(valid_h)})")

        if conflicts:
            n_resolved = len(resolved_map)
            summary_lines.append(f"Conflicts: {len(conflicts)} total, {n_resolved} resolved, {unresolved} pending review")

        # Per-type breakdown
        for qa_type_label in ("single-evidence", "multi-evidence"):
            subset_c = []
            subset_h = []
            for i, v in enumerate(voted):
                if v.get("type") != qa_type_label:
                    continue
                c = v["correctness"]
                if c is None and i in resolved_map:
                    c = resolved_map[i]
                if c is not None:
                    subset_c.append(c)
                if v["hallucination"] is not None:
                    subset_h.append(v["hallucination"])
            if subset_c:
                avg = sum(subset_c) / len(subset_c)
                h_r = sum(1 for h in subset_h if h == 1) / len(subset_h) if subset_h else 0
                summary_lines.append(f"  {qa_type_label} ({len(subset_c)}): correctness={avg:.1%}, hallucination={h_r:.1%}")

    # --- Pivot table ---
    # Collect voted data by (species, mode)
    voted_by = {}  # (species, mode) -> list of voted items with resolved conflicts
    for species, mode in sorted_combos:
        voted_file = JUDGE_DIR / f"judge_{species}_{mode}_voted.json"
        if not voted_file.exists():
            continue
        data = json.loads(voted_file.read_text(encoding="utf-8"))

        # Load resolved conflicts
        cf_file = JUDGE_DIR / f"judge_{species}_{mode}_conflicts.json"
        resolved_map = {}
        if cf_file.exists():
            cf_data = json.loads(cf_file.read_text(encoding="utf-8"))
            for cf in cf_data:
                if cf.get("resolved_correctness") is not None:
                    resolved_map[cf["index"]] = cf["resolved_correctness"]

        # Apply resolved values
        for i, v in enumerate(data):
            if v["correctness"] is None and i in resolved_map:
                v["correctness"] = resolved_map[i]

        voted_by[(species, mode)] = data

    def calc_metrics(items):
        """Calculate (n, avg_correctness, hallucination_rate) for a list of voted items."""
        c_vals = [v["correctness"] for v in items if v["correctness"] is not None]
        h_vals = [v["hallucination"] for v in items if v["hallucination"] is not None]
        n = len(items)
        avg_c = sum(c_vals) / len(c_vals) if c_vals else None
        h_rate = sum(1 for h in h_vals if h == 1) / len(h_vals) if h_vals else None
        return n, avg_c, h_rate

    # Build pivot rows: one column per mode
    ALL_MODES = ["rag", "without_rag_mistral", "without_rag_deepseek", "without_rag_qwen2.5", "without_rag_llama3.3"]
    present_modes = [m for m in ALL_MODES if any(mode == m for _, mode in voted_by.keys())]
    species_list = sorted(set(s for s, m in voted_by.keys()))
    rows = []

    for species in species_list:
        for type_label in ("single-evidence", "multi-evidence"):
            row_data = {m: [v for v in voted_by.get((species, m), []) if v.get("type") == type_label]
                        for m in present_modes}
            rows.append((f"{species} / {type_label}", row_data))
        row_data = {m: voted_by.get((species, m), []) for m in present_modes}
        rows.append((f"{species} / ALL", row_data))

    # Total row
    total_data = {m: [v for s, mode in voted_by if mode == m for v in voted_by[(s, mode)]]
                  for m in present_modes}
    rows.append(("ALL", total_data))

    # Format table
    MODE_LABELS = {
        "rag": "RAG(Mistral)",
        "without_rag_mistral": "Mistral",
        "without_rag_deepseek": "DeepSeek",
        "without_rag_qwen2.5": "Qwen2.5",
        "without_rag_llama3.3": "Llama3.3",
    }
    col_w = 30
    col_data_w = 23  # Items Corr Hall per column

    summary_lines.append(f"\n{'='*60}")
    summary_lines.append("PIVOT TABLE")
    summary_lines.append(f"{'='*60}")

    header = f"{'':>{col_w}}"
    sub_header = f"{'':>{col_w}}"
    sep = f"{'-'*col_w}"
    for m in present_modes:
        label = MODE_LABELS.get(m, m.upper())
        header += f" | {label:^{col_data_w}}"
        sub_header += f" | {'Items':>5} {'Corr':>6} {'Hall':>7}"
        sep += f"-+-{'-'*col_data_w}"

    summary_lines.append(header)
    summary_lines.append(sub_header)
    summary_lines.append(sep)

    for label, row_data in rows:
        line = f"{label:>{col_w}}"
        for m in present_modes:
            n, avg_c, h_rate = calc_metrics(row_data[m])
            c_str = f"{avg_c:.1%}" if avg_c is not None else "  -  "
            h_str = f"{h_rate:.1%}" if h_rate is not None else "  -  "
            line += f" | {n:>5} {c_str:>6} {h_str:>7}"
        summary_lines.append(line)

    # Save summary
    summary_text = "\n".join(summary_lines)
    summary_file = JUDGE_DIR / "judge_summary.txt"
    summary_file.write_text(summary_text, encoding="utf-8")
    print(f"\n{'='*60}")
    print(summary_text)
    print(f"\nSummary saved to: {summary_file}")


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Multi-model voting judge for correctness + hallucination"
    )
    parser.add_argument("--species", choices=["mouse", "macaque"],
                        help="Species to evaluate")
    parser.add_argument("--mode", choices=["rag", "without_rag_mistral", "without_rag_deepseek", "without_rag_qwen2.5", "without_rag_llama3.3"],
                        help="rag / without_rag_mistral / without_rag_deepseek / without_rag_qwen2.5 / without_rag_llama3.3")
    parser.add_argument("--vote", action="store_true",
                        help="Run majority voting on existing per-model results")
    args = parser.parse_args()

    if args.vote:
        run_vote()
    elif args.species and args.mode:
        run_evaluate(args.species, args.mode)
    else:
        parser.error("Either --vote, or both --species and --mode are required.")


if __name__ == "__main__":
    main()
