#!/usr/bin/env python
"""
API model evaluation script for comparing commercial closed-source models
on the NeuroTools function-calling benchmark.

Supported providers: openai, anthropic, google, qwen, deepseek, llama
All providers use an OpenAI-compatible interface.

Setup:
  cp api_config.json.example api_config.json
  # fill in your API keys and base URLs

Usage:
  python eval_api_models.py \\
      --provider openai \\
      --prompt_strategy unified \\
      --dataset_path data/test.json

  # Retry failed samples
  python eval_api_models.py \\
      --provider openai \\
      --prompt_strategy unified \\
      --retry_failed results/openai_..._failed.json \\
      --merge_results results/openai_..._predictions.json
"""

import argparse
import json
import os
import sys
from typing import List, Dict, Optional
from tqdm import tqdm
from datasets import load_dataset
import time

from eval_custom import (
    classify_dataset_type,
    classify_task_type,
    check_correctness,
    compute_accuracy,
    print_accuracy_table,
)


# ============================================================
# API interface
# ============================================================

def load_api_config(config_file: str) -> dict:
    if not os.path.exists(config_file):
        raise FileNotFoundError(
            f"Config file {config_file} not found.\n"
            f"Please copy api_config.json.example to api_config.json and fill in your API keys."
        )
    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)


def clean_tools_enums(tools: List[dict]) -> List[dict]:
    """
    Remove unsupported fields from tool definitions for Gemini API.
    Gemini rejects: empty enum arrays, 'minimum', 'maximum', 'strict'.
    Only affects the tools parameter sent to the API — prompts remain unchanged.
    """
    if not tools:
        return tools

    # Keys unsupported by Gemini in parameter property definitions
    UNSUPPORTED_KEYS = {"minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
                        "multipleOf", "minLength", "maxLength", "pattern",
                        "minItems", "maxItems", "uniqueItems"}

    def clean_value(value):
        if isinstance(value, dict):
            cleaned = {}
            for key, val in value.items():
                if key == "enum" and isinstance(val, list) and len(val) == 0:
                    continue
                if key == "enum" and isinstance(val, list):
                    val = [v for v in val if v != ""]
                    if not val:
                        continue
                if key in UNSUPPORTED_KEYS:
                    continue
                cleaned[key] = clean_value(val)
            return cleaned
        elif isinstance(value, list):
            return [clean_value(item) for item in value]
        else:
            return value

    cleaned_tools = []
    for tool in tools:
        cleaned_tool = clean_value(tool)
        if isinstance(cleaned_tool, dict) and "function" in cleaned_tool:
            func = cleaned_tool["function"]
            if isinstance(func, dict) and "strict" in func:
                func.pop("strict")
        cleaned_tools.append(cleaned_tool)

    return cleaned_tools


def call_api(messages: List[dict], tools: List[dict], config: dict, provider: str = None, max_retries: int = 5) -> Optional[str]:
    """
    Unified API call using OpenAI-compatible interface.
    Retries indefinitely on 429 rate-limit errors.
    Returns None on failure (API error), or the response string (may be empty if model returns nothing).
    """
    try:
        import openai
    except ImportError:
        raise ImportError("Please install openai: pip install openai")

    openai.api_key = config["api_key"]
    openai.base_url = config["base_url"]

    tools_to_send = tools
    if provider and "google" in provider.lower() and tools:
        tools_to_send = clean_tools_enums(tools)
        tools_to_send = json.loads(json.dumps(tools_to_send, ensure_ascii=False))

    attempt = 0
    while True:
        try:
            if tools_to_send:
                response = openai.chat.completions.create(
                    model=config["model"],
                    messages=messages,
                    tools=tools_to_send,
                    tool_choice="auto",
                    temperature=0.0,
                )
            else:
                response = openai.chat.completions.create(
                    model=config["model"],
                    messages=messages,
                    temperature=0.0,
                )

            message = response.choices[0].message
            if message.tool_calls:
                result = []
                for tool_call in message.tool_calls:
                    result.append({
                        "name": tool_call.function.name,
                        "arguments": json.loads(tool_call.function.arguments)
                    })
                return json.dumps(result, ensure_ascii=False)

            return message.content or ""

        except Exception as e:
            error_str = str(e)
            is_rate_limit = "429" in error_str or "RateLimitReached" in error_str

            if is_rate_limit:
                wait_time = min(30 * (attempt + 1), 300)
                print(f"\n[Rate limit] Attempt {attempt + 1}: waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                attempt += 1
                continue

            attempt += 1
            if attempt >= max_retries:
                print(f"\n[Error] Failed after {max_retries} attempts: {error_str}")
                return None

            wait_time = min(10 * attempt, 60)
            print(f"\n[Error] Attempt {attempt}: {error_str[:100]}. Retrying in {wait_time}s...")
            time.sleep(wait_time)


# ============================================================
# Input parsing and prompt strategies
# ============================================================

def parse_tools_from_input(input_text: str) -> List[dict]:
    """Parse the tools list from the 'input' field (format: 'tools: [...]')."""
    if not input_text or not input_text.startswith("tools:"):
        return []
    tools_json = input_text[7:]
    try:
        return json.loads(tools_json)
    except json.JSONDecodeError:
        return []


def tools_to_plain_text(tools: List[dict]) -> str:
    """Convert tools definitions to plain text (fallback for strict APIs)."""
    if not tools:
        return ""

    text_parts = ["Available functions you can call:"]
    for i, tool in enumerate(tools, 1):
        if "function" not in tool:
            continue
        func = tool["function"]
        text_parts.append(f"\n{i}. {func.get('name', 'unknown')}")
        text_parts.append(f"   Description: {func.get('description', '')}")
        params = func.get("parameters", {})
        if params.get("properties"):
            text_parts.append("   Parameters:")
            for param_name, param_info in params["properties"].items():
                required = param_name in params.get("required", [])
                req_mark = "[required]" if required else "[optional]"
                text_parts.append(
                    f"     - {param_name} ({param_info.get('type', 'unknown')}) "
                    f"{req_mark}: {param_info.get('description', '')}"
                )
    return "\n".join(text_parts)


def create_fewshot_examples() -> str:
    return """Here are some examples:

Example 1 (Zero task - plain text response):
User: "Hello, what can you do?"
Assistant: "I can help you query and visualize neuron data from mouse and macaque brain atlases."

Example 2 (Single task - one function call):
User: "use mouse line Thy1-YFP"
Tools: [{"type": "function", "function": {"name": "set_mouse_line", ...}}]
Assistant: [{"name":"set_mouse_line","arguments":{"mouse_line":"Thy1-YFP"}}]

Example 3 (Parallel task - multiple function calls):
User: "First set mouse line to Orexin, then query neurons with axon only"
Assistant: [{"name":"set_mouse_line","arguments":{"mouse_line":"Orexin"}},{"name":"query_neurons_by_structure","arguments":{"axon_and_dendrite":false,"axon_only":true}}]"""


def build_prompt_unified(instruction: str, input_text: str) -> tuple:
    """Unified strategy: simple user message with tools."""
    tools = parse_tools_from_input(input_text)
    messages = [{"role": "user", "content": instruction}]
    return messages, tools


def build_prompt_optimized(instruction: str, input_text: str) -> tuple:
    """Optimized strategy: system prompt with task description."""
    tools = parse_tools_from_input(input_text)
    system_prompt = (
        "You are a function calling assistant for neuroscience data visualization.\n"
        "Your task is to:\n"
        "1. If the user is just greeting or asking general questions, respond with plain text (do NOT call any function).\n"
        "2. If the user requests specific operations, call the appropriate functions with correct parameters.\n"
        "3. You can call multiple functions in sequence if needed.\n"
        "4. Always return function calls in JSON array format: [{\"name\": \"func_name\", \"arguments\": {...}}]"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": instruction},
    ]
    return messages, tools


def build_prompt_fewshot(instruction: str, input_text: str) -> tuple:
    """Few-shot strategy: system prompt with examples."""
    tools = parse_tools_from_input(input_text)
    system_prompt = (
        "You are a function calling assistant for neuroscience data visualization.\n"
        "Analyze user requests and call appropriate functions or respond with text.\n\n"
        + create_fewshot_examples()
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": instruction},
    ]
    return messages, tools


# ============================================================
# Main evaluation loop
# ============================================================

def generate_predictions_api(
    provider: str,
    config: dict,
    dataset,
    prompt_strategy: str,
    num_print: int = 3,
    output_dir: str = "results",
    resume_from: Optional[str] = None,
    request_interval: float = 1.5,
) -> tuple:
    """Generate predictions via API with checkpoint support for resuming."""
    build_prompt = {
        "unified": build_prompt_unified,
        "optimized": build_prompt_optimized,
        "fewshot": build_prompt_fewshot,
    }[prompt_strategy]

    safe_model = config["model"].replace("/", "-").replace(":", "-")
    base = f"{provider}_{safe_model}_{prompt_strategy}"
    checkpoint_file = os.path.join(output_dir, f"{base}_checkpoint.json")
    failed_file = os.path.join(output_dir, f"{base}_failed.json")

    predictions: List[str] = []
    failed_indices: List[int] = []
    start_idx = 0

    # Resume from checkpoint
    resume_path = resume_from or (checkpoint_file if os.path.exists(checkpoint_file) else None)
    if resume_path and os.path.exists(resume_path):
        print(f"Resuming from checkpoint: {resume_path}")
        with open(resume_path, "r", encoding="utf-8") as f:
            ckpt = json.load(f)
            predictions = ckpt.get("predictions", [])
            failed_indices = ckpt.get("failed_indices", [])
            start_idx = len(predictions)
        print(f"Resuming from sample {start_idx}/{len(dataset)}")

    for i in tqdm(range(start_idx, len(dataset)), desc=f"{provider}/{prompt_strategy}",
                  initial=start_idx, total=len(dataset)):
        instruction = dataset[i]["instruction"]
        input_text = dataset[i]["input"]

        messages, tools = build_prompt(instruction, input_text)
        pred = call_api(messages, tools, config, provider)
        if pred is None:
            pred = ""
            failed_indices.append(i)
            print(f"\n[Warning] Sample {i} failed, recorded to failed list")
        predictions.append(pred)

        if num_print < 0 or i < num_print:
            target = dataset[i]["output"]
            task_type = classify_task_type(target)
            is_correct = check_correctness(pred, target, task_type)
            print(f"\nSample {i}:")
            print(f"  Instruction: {instruction[:100]}...")
            print(f"  Target:  {target}")
            print(f"  Predict: {pred}")
            print(f"  Correct: {is_correct}")

        # Save checkpoint every 50 samples
        if (i + 1) % 50 == 0:
            with open(checkpoint_file, "w", encoding="utf-8") as f:
                json.dump({"predictions": predictions, "failed_indices": failed_indices, "last_index": i},
                          f, ensure_ascii=False, indent=2)
            print(f"\n[Checkpoint] Saved at {i + 1}/{len(dataset)}")

        time.sleep(request_interval)

    if failed_indices:
        with open(failed_file, "w", encoding="utf-8") as f:
            json.dump({
                "failed_indices": failed_indices,
                "total_failed": len(failed_indices),
                "dataset_info": [
                    {"index": idx, "instruction": dataset[idx]["instruction"],
                     "input": dataset[idx]["input"], "target": dataset[idx]["output"]}
                    for idx in failed_indices
                ]
            }, f, ensure_ascii=False, indent=2)
        print(f"\n[Failed] {len(failed_indices)} samples failed, saved to {failed_file}")

    if os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)

    return predictions, failed_indices


def main():
    parser = argparse.ArgumentParser(description="Evaluate API models on the NeuroTools function-calling benchmark")
    parser.add_argument("--provider", type=str, required=True,
                        choices=["openai", "anthropic", "google", "qwen", "deepseek", "llama"])
    parser.add_argument("--prompt_strategy", type=str, default="unified",
                        choices=["unified", "optimized", "fewshot"])
    parser.add_argument("--dataset_path", type=str, default="data/test.json")
    parser.add_argument("--config_file", type=str, default="api_config.json")
    parser.add_argument("--num_print", type=int, default=3,
                        help="Number of samples to print (-1 = all)")
    parser.add_argument("--output_dir", type=str, default="results")
    parser.add_argument("--resume_from", type=str, default=None,
                        help="Path to checkpoint file to resume from")
    parser.add_argument("--request_interval", type=float, default=1.5,
                        help="Seconds between API requests (default: 1.5)")
    parser.add_argument("--retry_failed", type=str, default=None,
                        help="Path to failed-indices file to retry")
    parser.add_argument("--merge_results", type=str, default=None,
                        help="Path to original predictions file to merge retry results into")
    parser.add_argument("--model", type=str, default=None,
                        help="Override model name from config file")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # ── Retry mode ────────────────────────────────────────────────────────────
    if args.retry_failed:
        print(f"\n{'='*60}\nRetry failed samples mode\n{'='*60}\n")

        if not os.path.exists(args.retry_failed):
            raise FileNotFoundError(f"Failed indices file not found: {args.retry_failed}")

        with open(args.retry_failed, "r", encoding="utf-8") as f:
            failed_data = json.load(f)
            failed_indices = failed_data["failed_indices"]

        print(f"Loaded {len(failed_indices)} failed samples")

        if not args.merge_results:
            raise ValueError("--merge_results is required in retry mode")
        if not os.path.exists(args.merge_results):
            raise FileNotFoundError(f"Original predictions file not found: {args.merge_results}")

        api_config = load_api_config(args.config_file)
        if args.provider not in api_config:
            raise ValueError(f"Provider {args.provider} not found in config file")

        provider_config = api_config[args.provider]
        if args.model:
            provider_config["model"] = args.model
        model_name = provider_config["model"]
        safe_model = model_name.replace("/", "-").replace(":", "-")

        dataset = load_dataset("json", data_files=args.dataset_path, split="train")
        build_prompt = {"unified": build_prompt_unified,
                        "optimized": build_prompt_optimized,
                        "fewshot": build_prompt_fewshot}[args.prompt_strategy]

        with open(args.merge_results, "r", encoding="utf-8") as f:
            predictions_data = json.load(f)

        max_rounds = 10
        remaining = list(failed_indices)

        for round_num in range(1, max_rounds + 1):
            if not remaining:
                break
            print(f"\n--- Retry round {round_num}/{max_rounds}: {len(remaining)} samples ---")

            still_failed = []
            for idx in tqdm(remaining, desc=f"Round {round_num}"):
                messages, tools = build_prompt(dataset[idx]["instruction"], dataset[idx]["input"])
                pred = call_api(messages, tools, provider_config, args.provider)
                if pred is None:
                    still_failed.append(idx)
                    print(f"\n[Warning] Sample {idx} failed in round {round_num}")
                else:
                    # Merge successful result immediately (pred may be "" if model returned empty)
                    predictions_data[idx]["predict"] = pred
                    task_type = classify_task_type(predictions_data[idx]["target"])
                    predictions_data[idx]["is_correct"] = check_correctness(
                        pred, predictions_data[idx]["target"], task_type)
                    print(f"\nRound {round_num} index {idx}: {pred}")
                time.sleep(args.request_interval)

            # Save merged predictions after each round
            with open(args.merge_results, "w", encoding="utf-8") as f:
                json.dump(predictions_data, f, ensure_ascii=False, indent=2)
            print(f"[Round {round_num}] Merged predictions saved ({len(remaining) - len(still_failed)} recovered)")

            remaining = still_failed
            if not remaining:
                print(f"[Round {round_num}] All samples recovered!")
                break

        # Recompute final metrics
        predictions = [item["predict"] for item in predictions_data]
        targets = [item["target"] for item in predictions_data]
        instructions = [item["instruction"] for item in predictions_data]
        inputs = [item["input"] for item in predictions_data]

        accuracy_dict = compute_accuracy(predictions, targets, instructions, inputs)
        print_accuracy_table(accuracy_dict["results"])

        metrics_file = os.path.join(args.output_dir,
                                    f"{args.provider}_{safe_model}_{args.prompt_strategy}_metrics.json")
        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(accuracy_dict, f, ensure_ascii=False, indent=2)
        print(f"Updated metrics saved to {metrics_file}")

        table_file = os.path.join(args.output_dir,
                                  f"{args.provider}_{safe_model}_{args.prompt_strategy}_accuracy_table.txt")
        orig_stdout = sys.stdout
        with open(table_file, "w", encoding="utf-8") as f:
            sys.stdout = f
            print_accuracy_table(accuracy_dict["results"])
            sys.stdout = orig_stdout
        print(f"Accuracy table saved to {table_file}")

        # Update failed file: keep only still-remaining failures
        failed_file = os.path.join(args.output_dir,
                                   f"{args.provider}_{safe_model}_{args.prompt_strategy}_failed.json")
        if remaining:
            with open(failed_file, "w", encoding="utf-8") as f:
                json.dump({
                    "failed_indices": remaining,
                    "total_failed": len(remaining),
                    "dataset_info": [
                        {"index": idx, "instruction": dataset[idx]["instruction"],
                         "input": dataset[idx]["input"], "target": dataset[idx]["output"]}
                        for idx in remaining
                    ]
                }, f, ensure_ascii=False, indent=2)
            print(f"[Still failed after {max_rounds} rounds] {len(remaining)} samples saved to {failed_file}")
        else:
            if os.path.exists(failed_file):
                os.remove(failed_file)
            print("All failed samples recovered. Failed file removed.")

        print(f"\n{'='*60}\nRetry complete!\n{'='*60}\n")
        return

    # ── Normal evaluation mode ────────────────────────────────────────────────
    api_config = load_api_config(args.config_file)
    if args.provider not in api_config:
        raise ValueError(f"Provider {args.provider} not found in config file")

    provider_config = api_config[args.provider]
    if args.model:
        provider_config["model"] = args.model
    model_name = provider_config["model"]

    print(f"\n{'='*60}")
    print(f"Evaluation config:")
    print(f"  Provider:        {args.provider}")
    print(f"  Model:           {model_name}")
    print(f"  Prompt strategy: {args.prompt_strategy}")
    print(f"  Dataset:         {args.dataset_path}")
    print(f"{'='*60}\n")

    dataset = load_dataset("json", data_files=args.dataset_path, split="train")
    targets = dataset["output"]
    instructions = dataset["instruction"]
    inputs = dataset["input"]

    predictions, failed_indices = generate_predictions_api(
        args.provider, provider_config, dataset, args.prompt_strategy,
        args.num_print, args.output_dir, args.resume_from, args.request_interval
    )

    if failed_indices:
        print(f"\n{'='*60}")
        print(f"Warning: {len(failed_indices)} samples failed")
        print(f"Failed indices: {failed_indices[:10]}{'...' if len(failed_indices) > 10 else ''}")
        print(f"Use --retry_failed to re-run failed samples")
        print(f"{'='*60}\n")

    accuracy_dict = compute_accuracy(predictions, targets, instructions, inputs)
    print_accuracy_table(accuracy_dict["results"])

    safe_model = model_name.replace("/", "-").replace(":", "-")
    base_filename = f"{args.provider}_{safe_model}_{args.prompt_strategy}"

    metrics_file = os.path.join(args.output_dir, f"{base_filename}_metrics.json")
    bad_cases_file = os.path.join(args.output_dir, f"{base_filename}_bad_cases.json")
    predictions_file = os.path.join(args.output_dir, f"{base_filename}_predictions.json")
    table_file = os.path.join(args.output_dir, f"{base_filename}_accuracy_table.txt")

    with open(table_file, "w", encoding="utf-8") as f:
        orig_stdout = sys.stdout
        sys.stdout = f
        print_accuracy_table(accuracy_dict["results"])
        sys.stdout = orig_stdout
    print(f"Accuracy table saved to {table_file}")

    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(accuracy_dict, f, indent=2, ensure_ascii=False)
    print(f"Metrics saved to {metrics_file}")

    bad_cases = [d for d in accuracy_dict["details"] if not d["is_correct"]]
    if bad_cases:
        with open(bad_cases_file, "w", encoding="utf-8") as f:
            json.dump(bad_cases, f, indent=2, ensure_ascii=False)
        print(f"Bad cases saved to {bad_cases_file} ({len(bad_cases)} cases)")
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
    with open(predictions_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"Predictions saved to {predictions_file}")


if __name__ == "__main__":
    main()

