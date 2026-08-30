"""
Test API connectivity for various models.

Usage:
  python scripts/test_api.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env")

# Read all model configs from .env
MODELS = {}
for prefix in ("DEEPSEEK", "OPENAI", "ANTHROPIC", "GEMINI"):
    api_key = os.getenv(f"{prefix}_API_KEY", "")
    base_url = os.getenv(f"{prefix}_BASE_URL", "")
    model = os.getenv(f"{prefix}_MODEL", "")
    if api_key and base_url and model:
        MODELS[prefix.lower()] = {
            "api_key": api_key,
            "base_url": base_url,
            "model": model,
        }

# Models used by HippoRAG (LLM + Embedding)
llm_base_url = os.getenv("BASE_URL", "")
llm_model = os.getenv("LLM_MODEL", "")
embedding_base_url = os.getenv("BASE_URL", "")
embedding_model = os.getenv("EMBEDDING_MODEL", "")
if llm_base_url and llm_model:
    MODELS["hipporag_llm"] = {
        "api_key": "sk-",
        "base_url": llm_base_url,
        "model": llm_model,
    }
if embedding_base_url and embedding_model:
    MODELS["hipporag_embedding"] = {
        "api_key": "sk-",
        "base_url": embedding_base_url,
        "model": embedding_model,
    }

# Cluster Ollama models (Qwen3-235B + Llama3.3)
cluster_base_url = os.getenv("CLUSTER_BASE_URL", "")
qwen2_5_model = os.getenv("QWEN2_5_MODEL", "")
llama33_model = os.getenv("LLAMA33_MODEL", "")
if cluster_base_url and qwen2_5_model:
    MODELS["cluster_qwen2.5"] = {
        "api_key": "ollama",
        "base_url": cluster_base_url,
        "model": qwen2_5_model,
    }
if cluster_base_url and llama33_model:
    MODELS["cluster_llama3.3"] = {
        "api_key": "ollama",
        "base_url": cluster_base_url,
        "model": llama33_model,
    }


def test_chat(name: str, config: dict) -> bool:
    """Test the chat completion API"""
    try:
        client = OpenAI(api_key=config["api_key"], base_url=config["base_url"])
        response = client.chat.completions.create(
            model=config["model"],
            messages=[{"role": "user", "content": "Hi, reply with just 'OK'."}],
            max_tokens=10,
        )
        # Handle different relay response formats
        if isinstance(response, str):
            reply = response.strip()
        else:
            reply = response.choices[0].message.content.strip()
        print(f"  [OK] {name}: {config['model']} -> \"{reply}\"")
        return True
    except Exception as e:
        print(f"  [FAIL] {name}: {config['model']} -> {type(e).__name__}: {e}")
        return False


def main():
    print("=== API Connectivity Test ===\n")

    if not MODELS:
        print("No model configs found, please check the .env file.")
        return

    success = 0
    total = len(MODELS)

    for name, config in MODELS.items():
        test_chat(name, config)
        success += 1

    print(f"\nResult: {success}/{total} model tests completed")


if __name__ == "__main__":
    main()
