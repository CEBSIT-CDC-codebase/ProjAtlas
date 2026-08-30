"""
Merge script: merges QA data, retrieval results, and without-RAG answers split by species
into unified files, for use by the eval scripts.

Usage:
  python scripts/merge_results.py

Input:
  output/all_qa_mouse.json + output/all_qa_macaque.json
  results/get_retrieved_chunks_output_mouse_top10.json + results/get_retrieved_chunks_output_macaque_top10.json
  results/without_rag_mouse.json + results/without_rag_macaque.json

Output:
  output/all_qa_merged.json
  results/get_retrieved_chunks_merged.json
  results/without_rag_merged.json
"""

import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
OUTPUT_DIR = ROOT_DIR / "output"
RESULTS_DIR = ROOT_DIR / "results"


def merge_qa():
    """Merge QA data for mouse + macaque"""
    all_qa = []

    for species in ("mouse", "macaque"):
        qa_file = OUTPUT_DIR / f"all_qa_{species}.json"
        if qa_file.exists():
            data = json.loads(qa_file.read_text(encoding="utf-8"))
            # Tag each QA entry with its source species
            for item in data:
                item["species"] = species
            all_qa.extend(data)
            print(f"  {species}: {len(data)} QA pairs")
        else:
            print(f"  {species}: not found, skipping")

    if all_qa:
        merged_path = OUTPUT_DIR / "all_qa_merged.json"
        merged_path.write_text(json.dumps(all_qa, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  -> {merged_path} ({len(all_qa)} total)")
    else:
        print("  No QA data found.")
    return all_qa


def merge_retrieved_chunks():
    """Merge retrieval results for mouse + macaque"""
    all_results = []

    for species in ("mouse", "macaque"):
        pattern = f"get_retrieved_chunks_output_{species}_top*.json"
        files = sorted(RESULTS_DIR.glob(pattern))
        for f in files:
            data = json.loads(f.read_text(encoding="utf-8"))
            # Tag each result with its source species
            for item in data:
                item["species"] = species
            all_results.extend(data)
            print(f"  {f.name}: {len(data)} entries")

    if all_results:
        merged_path = RESULTS_DIR / "get_retrieved_chunks_merged.json"
        merged_path.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  -> {merged_path} ({len(all_results)} total)")
    else:
        print("  No retrieval results found.")
    return all_results


def merge_without_rag():
    """Merge without-RAG answers for mouse + macaque"""
    all_results = []

    for species in ("mouse", "macaque"):
        f = RESULTS_DIR / f"without_rag_{species}.json"
        if f.exists():
            data = json.loads(f.read_text(encoding="utf-8"))
            for item in data:
                item["species"] = species
            all_results.extend(data)
            print(f"  {f.name}: {len(data)} entries")
        else:
            print(f"  without_rag_{species}.json: not found, skipping")

    if all_results:
        merged_path = RESULTS_DIR / "without_rag_merged.json"
        merged_path.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  -> {merged_path} ({len(all_results)} total)")
    else:
        print("  No without-RAG results found.")
    return all_results


def print_stats(qa_data: list, retrieved_data: list):
    """Print data statistics"""
    if not qa_data:
        return

    print(f"\n{'=' * 50}")
    print("Data statistics")
    print(f"{'=' * 50}")

    # Statistics by species
    for species in ("mouse", "macaque"):
        species_qa = [q for q in qa_data if q.get("species") == species]
        if not species_qa:
            continue
        single = sum(1 for q in species_qa if "single" in q.get("type", ""))
        multi = sum(1 for q in species_qa if "multi" in q.get("type", ""))
        print(f"\n{species}:")
        print(f"  QA pairs: {len(species_qa)} (single: {single}, multi: {multi})")

        species_ret = [r for r in retrieved_data if r.get("species") == species]
        if species_ret:
            print(f"  Retrieved: {len(species_ret)} entries")

    # Totals
    total_single = sum(1 for q in qa_data if "single" in q.get("type", ""))
    total_multi = sum(1 for q in qa_data if "multi" in q.get("type", ""))
    print(f"\nTotal: {len(qa_data)} QA pairs (single: {total_single}, multi: {total_multi})")
    if retrieved_data:
        print(f"Total: {len(retrieved_data)} retrieved entries")


def main():
    print("=== Merging QA data ===")
    qa_data = merge_qa()

    print("\n=== Merging retrieval results ===")
    RESULTS_DIR.mkdir(exist_ok=True)
    retrieved_data = merge_retrieved_chunks()

    print("\n=== Merging without-RAG answers ===")
    merge_without_rag()

    print_stats(qa_data, retrieved_data)

    print("\nDone. You can now run the evaluation scripts under eval/.")


if __name__ == "__main__":
    main()
