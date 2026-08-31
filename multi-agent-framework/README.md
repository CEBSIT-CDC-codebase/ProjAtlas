# multi-agent-framework

Part of the [ProjAtlas](../) code repository. Implements the multi-agent framework behind
ProjAtlas's conversational assistant (see paper Methods: "Multi-agent framework"):

- **Paper interpretation agent** — RAG-grounded literature Q&A over a curated neuroscience
  corpus (see [`../rag-evaluation`](../rag-evaluation) for the corresponding benchmark and
  evaluation).
- **Neuron selection agent** and **brain visualization agent** — translate natural-language
  instructions into structured function calls via a fine-tuned model (see
  [`../function-calling`](../function-calling) for training and evaluation).
- **Textual summarization agent** — generates natural-language reports from quantitative
  analyses of selected neurons (soma distribution, projection overview, and axon
  length-/terminal count-weighted projection heatmaps).

## Python

- Python 3.10

## Dependencies

- [HippoRAG](https://github.com/OSU-NLP-Group/HippoRAG) (MIT License)
- openai

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OpenAI-compatible endpoint, API key, and model names
```

`FUNCTION_CALLING_MODEL` in `.env` points to the fine-tuned model used by the neuron
selection and brain visualization agents. This model must be deployed separately (e.g.
via vLLM) and reachable at the endpoint configured by `BASE_URL`/`API_KEY`. The model
weights and deployment instructions are in
[`../function-calling/README.md`](../function-calling/README.md#fine-tuned-model-weights).

## Data

The paper interpretation agent's RAG knowledge base is built from:

1. Neuroscience publications, converted to Markdown (e.g. with [marker](https://github.com/VikParuchuri/marker))
   — see [`../rag-evaluation/data/SOURCE_PAPERS.md`](../rag-evaluation/data/SOURCE_PAPERS.md)
   for the paper list and [`data/RAG-md-mouse/README.md`](data/RAG-md-mouse/README.md) /
   [`data/RAG-md-macaque/README.md`](data/RAG-md-macaque/README.md) for where to place them.
   Full text is not redistributed in this repository due to publisher copyright.
2. `data/RAG-md-docs/` — the ProjAtlas platform's own user guide (included in full).
3. An offline HippoRAG index built from the above (generated locally, not tracked in git;
   see `.gitignore`).

## Architecture

All four agents are implemented as one `ChatSession` class (`assistant.py`) that dispatches
on the `task` field of the incoming `UserInput`. Agents share a single per-user
conversation history and a single OpenAI-compatible endpoint, but route to different
models: `FUNCTION_CALLING_MODEL` for the two function-calling agents, `LLM_MODEL` for
everything else.

```mermaid
flowchart TB
    IN["UserInput<br/>id · task · content<br/>neurons · regions · matrix"]
    DISPATCH{"send_message()<br/>dispatch on task"}
    HIST[("per-user session<br/>messages + tool_calls_indices")]
    OUT["AssistantMessage<br/>content + tool_calls"]

    IN --> DISPATCH
    DISPATCH <--> HIST

    subgraph PAPER["Paper interpretation agent"]
        direction TB
        P1["task: paper"] --> RM["HippoRAG index<br/>data/rag-mouse<br/>qa_top_k = 10"]
        P2["task: paper-macaque"] --> RQ["HippoRAG index<br/>data/rag-macaque<br/>qa_top_k = 10"]
        RM --> RAGQA["rag_qa()<br/>retrieve → generate"]
        RQ --> RAGQA
    end

    subgraph FC["Neuron selection + brain visualization agents"]
        direction TB
        F1["task: form"] --> T1["function_calling/form.py<br/>5 mouse tools"]
        F2["task: form-macaque"] --> T2["function_calling/form_macaque.py<br/>6 macaque tools"]
        F3["task: neuroviz"] --> T3["function_calling/neuroviz.py<br/>13 viewer tools"]
        T1 --> PTC["process_tool_calls()<br/>normalise to tool_calls"]
        T2 --> PTC
        T3 --> PTC
    end

    subgraph SUM["Textual summarization agent"]
        direction TB
        S1["task: summarization/*"] --> SP["prompt builders in summarization/<br/>soma_distribution · projection<br/>axon-length heatmap · terminal-count heatmap"]
    end

    DISPATCH --> P1 & P2 & F1 & F2 & F3 & S1
    DISPATCH -->|"any other task"| CHAT["general conversation<br/>plain chat completion"]

    RAGQA --> LLM["LLM_MODEL"]
    SP --> LLM
    CHAT --> LLM
    PTC --> FCM["FUNCTION_CALLING_MODEL"]

    LLM --> EP{{"OpenAI-compatible endpoint<br/>BASE_URL · API_KEY"}}
    FCM --> EP
    EP --> OUT
```

## Citation

See the [repository root README](../README.md#citation) for the current citation.
