"""
Without-RAG control experiment: generate baseline answers.
Has the LLM answer questions directly without retrieval context, to compare
the effect of RAG on answer quality.

Usage:
  Use ACTIVE_MODEL by default:
    python scripts/generate_without_rag.py --species mouse

  Specify a cluster model:
    python scripts/generate_without_rag.py --species mouse --model mistral
    python scripts/generate_without_rag.py --species mouse --model deepseek
    python scripts/generate_without_rag.py --species mouse --model qwen2.5
    python scripts/generate_without_rag.py --species mouse --model llama3.3

Output:
  results/without_rag_{species}_mistral.json   (Mistral-Small-3.1-24B)
  results/without_rag_{species}_deepseek.json  (DeepSeek-v4-pro)
  results/without_rag_{species}_qwen2.5.json   (Qwen2.5-72B)
  results/without_rag_{species}_llama3.3.json  (Llama3.3)
"""

import argparse
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Project root directory
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env")


SYSTEM_PROMPT = (
    "You are a scientific Q&A assistant specializing in neuroscience. "
    "Answer the question directly and concisely based on your general knowledge."
)

# Cluster model config (ollama, no API key needed)
CLUSTER_MODELS = {
    "qwen2.5": {
        "base_url": os.getenv("CLUSTER_BASE_URL", ""),
        "model": os.getenv("QWEN2_5_MODEL", "qwen2.5:72b"),
        "api_key": "ollama",
    },
    "llama3.3": {
        "base_url": os.getenv("CLUSTER_BASE_URL", ""),
        "model": os.getenv("LLAMA33_MODEL", "llama3.3"),
        "api_key": "ollama",
    },
    "mistral": {
        "base_url": os.getenv("BASE_URL", ""),
        "model": os.getenv("LLM_MODEL", ""),
        "api_key": "ollama",
    },
    "deepseek": {
        "base_url": os.getenv("DEEPSEEK_BASE_URL", ""),
        "model": os.getenv("DEEPSEEK_MODEL", ""),
        "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
    },
}


def get_model_config(model_name: str | None) -> tuple[str, str, str]:
    """Return the (base_url, api_key, model) tuple."""
    if model_name and model_name in CLUSTER_MODELS:
        cfg = CLUSTER_MODELS[model_name]
        return cfg["base_url"], cfg["api_key"], cfg["model"]
    # Default: ACTIVE_MODEL
    prefix = os.getenv("ACTIVE_MODEL", "deepseek").upper()
    return (
        os.getenv(f"{prefix}_BASE_URL", ""),
        os.getenv(f"{prefix}_API_KEY", ""),
        os.getenv(f"{prefix}_MODEL", ""),
    )

def ask(client: OpenAI, model: str, question: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def main():
    parser = argparse.ArgumentParser(description="Without-RAG baseline")
    parser.add_argument("--species", choices=["mouse", "macaque"], required=True,
                        help="Species to process (required)")
    parser.add_argument("--model", choices=["mistral", "deepseek", "qwen2.5", "llama3.3"], default=None,
                        help="Model to use: mistral/deepseek (via ollama/API) or qwen2.5/llama3.3 (cluster ollama). "
                             "Default: ACTIVE_MODEL from .env")
    args = parser.parse_args()

    base_url, api_key, model = get_model_config(args.model)

    # Read the QA file for the corresponding species
    qa_file = ROOT_DIR / "output" / f"all_qa_{args.species}.json"
    if not qa_file.exists():
        print(f"Error: {qa_file} not found.")
        print("Run scripts/generate_qa.py first.")
        return

    qa_data = json.loads(qa_file.read_text(encoding="utf-8"))
    questions = [qa["question"] for qa in qa_data]

    client = OpenAI(base_url=base_url, api_key=api_key)

    print(f"Species: {args.species}")
    print(f"Model: {model}")
    print(f"Number of questions: {len(questions)}")
    print(f"{'=' * 60}\n")

    # Resume support: check for existing results
    results_dir = ROOT_DIR / "results"
    results_dir.mkdir(exist_ok=True)
    suffix = f"_{args.model}" if args.model else ""
    output_path = results_dir / f"without_rag_{args.species}{suffix}.json"

    results = []
    if output_path.exists():
        results = json.loads(output_path.read_text(encoding="utf-8"))
    done_count = len(results)

    if done_count >= len(questions):
        print(f"Already complete ({done_count}/{len(questions)}), nothing to do.")
        return

    if done_count > 0:
        print(f"Resuming from {done_count}/{len(questions)}")

    for i, question in enumerate(questions[done_count:], done_count + 1):
        print(f"[{i}/{len(questions)}] {question[:60]}...")
        answer = ask(client, model, question)
        results.append({
            "question": question,
            "answer": answer,
        })
        output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  A: {answer[:80]}...\n")

    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
