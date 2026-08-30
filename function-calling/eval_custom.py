#!/usr/bin/env python
"""
Custom accuracy evaluation script for the NeuroTools function-calling benchmark.

Evaluation dimensions:
  Dataset type (inferred from the 'input' field): Mouse / Macaque / Neuroviz
  Task type    (inferred from the 'output' field): Zero / Single / Parallel
  → 3×3 = 9 fine-grained dimensions + per-type totals + overall accuracy

Evaluation rules:
  Zero     – model output is NOT valid JSON  → correct
  Single / Parallel – parse both prediction and target as JSON objects and
                      compare semantically (whitespace/indent differences ignored)

Usage (recommended: --template auto uses the model's native chat_template):

  # Evaluate fine-tuned model
  python eval_custom.py \\
      --model_name_or_path Salesforce/Llama-xLAM-2-8b-fc-r \\
      --hub modelscope \\
      --adapter_path saves/xlam-8b/lora/sft \\
      --dataset_path data/test.json \\
      --template auto \\
      --num_print -1

  # Evaluate base model (no adapter)
  python eval_custom.py \\
      --model_name_or_path Salesforce/Llama-xLAM-2-8b-fc-r \\
      --hub modelscope \\
      --adapter_path "" \\
      --dataset_path data/test.json \\
      --template auto
"""

import argparse
import json
import os
import sys
from typing import List, Dict, Optional

import torch
from datasets import load_dataset
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
from peft import PeftModel
try:
    from src.llamafactory.extras.misc import try_download_model_from_other_hub
    from src.llamafactory.hparams.model_args import ModelArguments
    _LLAMAFACTORY_AVAILABLE = True
except ImportError:
    _LLAMAFACTORY_AVAILABLE = False


# ============================================================
# Classification and comparison utilities
# ============================================================

def is_valid_json(s: str) -> bool:
    try:
        json.loads(s)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def classify_dataset_type(input_text: str) -> str:
    """
    Infer dataset type from tool names present in the input field.
      Mouse    – contains 'set_mouse_line'
      Macaque  – contains 'filter_neurons_by_hemisphere'
      Neuroviz – neither
    """
    if "set_mouse_line" in input_text:
        return "Mouse"
    elif "filter_neurons_by_hemisphere" in input_text:
        return "Macaque"
    else:
        return "Neuroviz"


def classify_task_type(target_output: str) -> str:
    """
    Infer task type from the number of function calls in the target output.
      Zero     – output is plain text (not valid JSON)
      Single   – exactly 1 function call
      Parallel – 2 or more function calls
    """
    try:
        parsed = json.loads(target_output)
    except (json.JSONDecodeError, TypeError):
        return "Zero"

    if isinstance(parsed, list):
        if len(parsed) == 0:
            return "Zero"
        elif len(parsed) == 1:
            return "Single"
        else:
            return "Parallel"
    else:
        return "Single"


def check_correctness(pred_str: str, target_str: str, task_type: str) -> bool:
    """
    Check whether a prediction is correct.

    Zero     – prediction must NOT be valid JSON.
    Single / Parallel – parse both as JSON and compare semantically.
                        Also handles mismatched outer-array wrapping.
    """
    pred_stripped = pred_str.strip()
    target_stripped = target_str.strip()

    if task_type == "Zero":
        return not is_valid_json(pred_stripped)

    try:
        target_obj = json.loads(target_stripped)
    except (json.JSONDecodeError, TypeError):
        return False

    try:
        pred_obj = json.loads(pred_stripped)
    except (json.JSONDecodeError, TypeError):
        return False

    if pred_obj == target_obj:
        return True

    # Handle array-wrapping mismatch
    if isinstance(target_obj, list) and len(target_obj) == 1 and not isinstance(pred_obj, list):
        if pred_obj == target_obj[0]:
            return True
    if isinstance(pred_obj, list) and len(pred_obj) == 1 and not isinstance(target_obj, list):
        if pred_obj[0] == target_obj:
            return True

    return False


# ============================================================
# Multi-dimensional accuracy computation
# ============================================================

DATASET_TYPES = ["Mouse", "Macaque", "Neuroviz"]
TASK_TYPES = ["Zero", "Single", "Parallel"]


def compute_accuracy(
    predictions: List[str],
    targets: List[str],
    instructions: List[str],
    inputs: List[str],
) -> dict:
    """
    Compute multi-dimensional accuracy.

    Returns:
    {
        "results": {
            "Mouse_Zero":     {"correct": N, "total": N, "accuracy": 0.xx},
            ...
            "Overall":        {...},
        },
        "details": [ per-sample dicts ]
    }
    """
    dim_stats: Dict[tuple, Dict[str, int]] = {}
    for dt in DATASET_TYPES:
        for tt in TASK_TYPES:
            dim_stats[(dt, tt)] = {"correct": 0, "total": 0}

    details = []

    for idx, (pred, target, instruction, input_text) in enumerate(
        zip(predictions, targets, instructions, inputs)
    ):
        dataset_type = classify_dataset_type(input_text)
        task_type = classify_task_type(target)
        correct = check_correctness(pred, target, task_type)

        dim_stats[(dataset_type, task_type)]["total"] += 1
        if correct:
            dim_stats[(dataset_type, task_type)]["correct"] += 1

        details.append({
            "index": idx,
            "instruction": instruction,
            "target": target,
            "prediction": pred,
            "dataset_type": dataset_type,
            "task_type": task_type,
            "is_correct": correct,
        })

    results: Dict[str, dict] = {}

    for dt in DATASET_TYPES:
        for tt in TASK_TYPES:
            s = dim_stats[(dt, tt)]
            results[f"{dt}_{tt}"] = {
                "correct": s["correct"],
                "total": s["total"],
                "accuracy": s["correct"] / s["total"] if s["total"] > 0 else 0.0,
            }

    for dt in DATASET_TYPES:
        total = sum(dim_stats[(dt, tt)]["total"] for tt in TASK_TYPES)
        correct = sum(dim_stats[(dt, tt)]["correct"] for tt in TASK_TYPES)
        results[f"{dt}_Total"] = {
            "correct": correct,
            "total": total,
            "accuracy": correct / total if total > 0 else 0.0,
        }

    for tt in TASK_TYPES:
        total = sum(dim_stats[(dt, tt)]["total"] for dt in DATASET_TYPES)
        correct = sum(dim_stats[(dt, tt)]["correct"] for dt in DATASET_TYPES)
        results[f"{tt}_Total"] = {
            "correct": correct,
            "total": total,
            "accuracy": correct / total if total > 0 else 0.0,
        }

    total_all = sum(s["total"] for s in dim_stats.values())
    correct_all = sum(s["correct"] for s in dim_stats.values())
    results["Overall"] = {
        "correct": correct_all,
        "total": total_all,
        "accuracy": correct_all / total_all if total_all > 0 else 0.0,
    }

    return {"results": results, "details": details}


def print_accuracy_table(results: dict) -> None:
    """Print a formatted multi-dimensional accuracy table."""

    def _fmt(key: str) -> str:
        r = results.get(key)
        if r is None or r["total"] == 0:
            return "   -/-  (  -  )"
        return f"{r['correct']:>3}/{r['total']:<3} ({r['accuracy']:.1%})"

    sep = "=" * 81
    print(f"\n{sep}")
    print("                         Evaluation Results")
    print(sep)

    header = f"{'':>12} {'Zero':>16} {'Single':>16} {'Parallel':>16} {'Total':>16}"
    print(header)
    print("-" * 81)

    for dt in DATASET_TYPES:
        row = f"{dt:>12}"
        for tt in TASK_TYPES:
            row += f" {_fmt(f'{dt}_{tt}'):>16}"
        row += f" {_fmt(f'{dt}_Total'):>16}"
        print(row)

    print("-" * 81)

    row = f"{'Total':>12}"
    for tt in TASK_TYPES:
        row += f" {_fmt(f'{tt}_Total'):>16}"
    row += f" {_fmt('Overall'):>16}"
    print(row)

    print(sep)

    overall = results["Overall"]
    print(f"\nOverall Accuracy: {overall['accuracy']:.4f}"
          f"  ({overall['correct']}/{overall['total']})")
    print()


# ============================================================
# Model loading and inference
# ============================================================

def get_stop_token_ids(tokenizer):
    """
    Collect all stop token IDs for the model.
    Covers both Llama 3 and Qwen2/ChatML families.
    """
    stop_ids = set()

    if tokenizer.eos_token_id is not None:
        stop_ids.add(tokenizer.eos_token_id)

    known_stop_tokens = [
        "<|eot_id|>",       # Llama 3 end-of-turn
        "<|end_of_text|>",  # Llama 3 end-of-text
        "<|eom_id|>",       # Llama 3 end-of-message
        "<|im_end|>",       # Qwen2/ChatML end
        "<|endoftext|>",    # Qwen2 end-of-text
    ]
    for token in known_stop_tokens:
        token_id = tokenizer.convert_tokens_to_ids(token)
        if token_id is not None and token_id != getattr(tokenizer, "unk_token_id", None):
            stop_ids.add(token_id)

    return list(stop_ids)


def load_model_and_tokenizer(model_name_or_path, hub="huggingface", adapter_path=None, template="auto", device_map="auto"):
    """
    Load model and tokenizer, optionally applying a LoRA adapter.

    Tokenizer loading priority:
    1. adapter_path (if it contains tokenizer_config.json) — LLaMA-Factory saves
       the tokenizer alongside the adapter with correct eos_token configuration.
    2. base model path.
    """
    print(f"Loading base model from {model_name_or_path} (hub: {hub})...")
    if hub == "modelscope":
        os.environ["USE_MODELSCOPE_HUB"] = "1"
    elif hub == "huggingface":
        os.environ["USE_MODELSCOPE_HUB"] = "0"

    if not _LLAMAFACTORY_AVAILABLE:
        raise ImportError(
            "LLaMA-Factory is required for local model evaluation.\n"
            "Run this script from inside the LLaMA-Factory root directory, "
            "or install it with: pip install -e .[torch]"
        )
    model_args = ModelArguments(
        model_name_or_path=model_name_or_path,
        cache_dir=None,
        model_revision="main",
        hf_hub_token=None,
        ms_hub_token=None,
    )
    downloaded_path = try_download_model_from_other_hub(model_args)
    print(f"Model will be loaded from: {downloaded_path}")

    auth_token = None
    if hub == "modelscope":
        auth_token = model_args.ms_hub_token
    elif hub == "huggingface":
        auth_token = model_args.hf_hub_token

    # Load tokenizer — prefer adapter path when available
    tokenizer_load_path = downloaded_path
    if adapter_path and os.path.isfile(os.path.join(adapter_path, "tokenizer_config.json")):
        tokenizer_load_path = adapter_path
        print(f"Loading tokenizer from adapter path: {adapter_path}")
    else:
        print(f"Loading tokenizer from base model: {downloaded_path}")

    tokenizer = AutoTokenizer.from_pretrained(
        tokenizer_load_path,
        trust_remote_code=True,
        token=auth_token,
    )

    has_chat_template = hasattr(tokenizer, "chat_template") and tokenizer.chat_template is not None
    print(f"Tokenizer info:")
    print(f"  eos_token: {tokenizer.eos_token!r} (id: {tokenizer.eos_token_id})")
    print(f"  pad_token: {tokenizer.pad_token!r} (id: {tokenizer.pad_token_id})")
    print(f"  has chat_template: {has_chat_template}")

    stop_ids = get_stop_token_ids(tokenizer)
    print(f"  stop token IDs: {stop_ids}")

    model = AutoModelForCausalLM.from_pretrained(
        downloaded_path,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        device_map=device_map,
        trust_remote_code=True,
        token=auth_token,
    )
    if adapter_path:
        print(f"Loading adapter from {adapter_path}...")
        model = PeftModel.from_pretrained(model, adapter_path)
        model = model.merge_and_unload()
    model.eval()
    return tokenizer, model


def format_input(tokenizer, template_name, instruction, input_text):
    """
    Format a single sample into a model prompt.

    template_name:
      auto    (recommended) – use the tokenizer's built-in chat_template
      llama3  – hardcoded Llama 3 format
      alpaca  – Alpaca instruction format
      default – raw content, no formatting
    """
    content = f"{instruction}\n{input_text}" if input_text else instruction

    if template_name == "auto":
        if hasattr(tokenizer, "chat_template") and tokenizer.chat_template is not None:
            messages = [{"role": "user", "content": content}]
            return tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        else:
            return content

    elif template_name == "llama3":
        return (
            "<|begin_of_text|>"
            "<|start_header_id|>user<|end_header_id|>\n\n"
            f"{content}"
            "<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n"
        )
    elif template_name == "alpaca":
        if input_text:
            return f"Instruction: {instruction}\nInput: {input_text}\nResponse:"
        else:
            return f"Instruction: {instruction}\nResponse:"
    else:
        return content


def generate_predictions(model, tokenizer, dataset, template, max_new_tokens, temperature, batch_size=1, num_print=3):
    """Generate predictions for the entire dataset."""
    predictions = []

    eos_ids = get_stop_token_ids(tokenizer)
    generation_config = GenerationConfig(
        max_new_tokens=max_new_tokens,
        do_sample=False,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=eos_ids,
    )

    for i in tqdm(range(len(dataset)), desc="Generating predictions"):
        instruction = dataset[i]["instruction"]
        input_text = dataset[i]["input"]
        prompt = format_input(tokenizer, template, instruction, input_text)

        if i == 0:
            print(f"\n--- First prompt preview (first 500 chars) ---")
            print(prompt[:500])
            print(f"--- End of preview ---\n")

        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        with torch.no_grad():
            outputs = model.generate(**inputs, generation_config=generation_config)
            pred = tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True
            ).strip()
        predictions.append(pred)

        if num_print < 0 or i < num_print:
            target = dataset[i]["output"]
            task_type = classify_task_type(target)
            is_correct = check_correctness(pred, target, task_type)
            print(f"Sample {i}:")
            print(f"  Target:  {target}")
            print(f"  Predict: {pred}")
            print(f"  Correct: {is_correct}")

    return predictions


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name_or_path", type=str, default="Salesforce/Llama-xLAM-2-8b-fc-r")
    parser.add_argument("--hub", type=str, default="modelscope", choices=["huggingface", "modelscope"])
    parser.add_argument("--adapter_path", type=str, default="saves/xlam-8b/lora/sft")
    parser.add_argument("--dataset_path", type=str, default="data/test.json")
    parser.add_argument("--template", type=str, default="auto",
                        help="auto (recommended) | llama3 | alpaca | default")
    parser.add_argument("--batch_size", type=int, default=1)
    parser.add_argument("--max_new_tokens", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--output_dir", type=str, default="results",
                        help="Directory to save all output files")
    parser.add_argument("--run_name", type=str, default=None,
                        help="Name prefix for output files (default: auto-generated from model/adapter)")
    parser.add_argument("--output_file", type=str, default=None,
                        help="Override output predictions file path")
    parser.add_argument("--num_print", type=int, default=3,
                        help="Number of samples to print (-1 = all)")
    parser.add_argument("--metrics_file", type=str, default=None,
                        help="Override metrics file path")
    parser.add_argument("--bad_cases_file", type=str, default=None,
                        help="Override bad cases file path")
    args = parser.parse_args()

    # Auto-generate run name from adapter_path or model name
    if args.run_name is None:
        if args.adapter_path:
            # e.g. saves/xlam-8b/lora/sft -> xlam_8b_finetuned
            _IGNORE = {"saves", "lora", "sft", "FunctionCalling-Model-SFT", "before-FunctionCalling-Model-SFT", "RESULT-FunctionCalling-Model-SFT"}
            parts = [p for p in args.adapter_path.replace("\\", "/").split("/") if p and p not in _IGNORE]
            args.run_name = "_".join(parts).replace("-", "_") + "_finetuned" if parts else "xlam_8b_finetuned"
        else:
            # base model
            model_short = args.model_name_or_path.split("/")[-1].replace("-", "_").lower()
            args.run_name = model_short + "_base"

    os.makedirs(args.output_dir, exist_ok=True)

    if args.output_file is None:
        args.output_file = os.path.join(args.output_dir, f"{args.run_name}_predictions.json")
    if args.metrics_file is None:
        args.metrics_file = os.path.join(args.output_dir, f"{args.run_name}_metrics.json")
    if args.bad_cases_file is None:
        args.bad_cases_file = os.path.join(args.output_dir, f"{args.run_name}_bad_cases.json")

    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
    if args.hub == "modelscope":
        os.environ["USE_MODELSCOPE_HUB"] = "1"
    elif args.hub == "huggingface":
        os.environ["USE_MODELSCOPE_HUB"] = "0"

    print(f"Loading dataset from {args.dataset_path}...")
    dataset = load_dataset("json", data_files=args.dataset_path, split="train")
    targets = dataset["output"]
    instructions = dataset["instruction"]
    inputs = dataset["input"]

    tokenizer, model = load_model_and_tokenizer(
        args.model_name_or_path, args.hub, args.adapter_path, args.template
    )

    predictions = generate_predictions(
        model, tokenizer, dataset, args.template,
        args.max_new_tokens, args.temperature, args.batch_size, args.num_print
    )

    accuracy_dict = compute_accuracy(predictions, targets, instructions, inputs)
    print_accuracy_table(accuracy_dict["results"])

    table_file = os.path.join(args.output_dir, f"{args.run_name}_accuracy_table.txt")
    orig_stdout = sys.stdout
    with open(table_file, "w", encoding="utf-8") as f:
        sys.stdout = f
        print_accuracy_table(accuracy_dict["results"])
        sys.stdout = orig_stdout
    print(f"Accuracy table saved to {table_file}")

    with open(args.metrics_file, "w", encoding="utf-8") as f:
        json.dump(accuracy_dict, f, indent=2, ensure_ascii=False)
    print(f"Metrics saved to {args.metrics_file}")

    bad_cases = [d for d in accuracy_dict["details"] if not d["is_correct"]]
    if bad_cases:
        with open(args.bad_cases_file, "w", encoding="utf-8") as f:
            json.dump(bad_cases, f, indent=2, ensure_ascii=False)
        print(f"Bad cases saved to {args.bad_cases_file} ({len(bad_cases)} cases)")
    else:
        print("No bad cases found.")

    output_data = [
        {
            "instruction": dataset[i]["instruction"],
            "input": dataset[i]["input"],
            "target": targets[i],
            "predict": predictions[i],
            "dataset_type": accuracy_dict["details"][i]["dataset_type"],
            "task_type": accuracy_dict["details"][i]["task_type"],
            "is_correct": accuracy_dict["details"][i]["is_correct"],
        }
        for i in range(len(dataset))
    ]
    with open(args.output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"Predictions saved to {args.output_file}")


if __name__ == "__main__":
    main()
