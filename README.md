# ProjAtlas

An AI-assisted multi-agent platform for interactive exploration of single-neuron
projectomes across mouse and macaque brains.

ProjAtlas integrates atlas-registered single-neuron projectomes from mouse and macaque
brains and supports literature interpretation, data querying, interactive visualization,
and quantitative analysis through natural-language interaction.

## Repository Structure

```
ProjAtlas/
├── platform/                  # ProjAtlas web platform
│   ├── frontend/              # Web client (interactive 3D visualization, data querying)
│   ├── backend/               # Backend services (user/session/message management, LLM assistant)
│   └── neuroviz-client/       # 3D brain visualization engine (if released)
├── multi-agent-framework/     # Multi-agent framework (paper-interpretation, neuron-selection,
│                               # brain-visualization, and textual-summarization agents)
├── rag-evaluation/            # RAG benchmark and evaluation (paper interpretation agent)
└── function-calling/          # Function-calling model training and evaluation
                                # (neuron-selection and brain-visualization agents)
```

Each subdirectory has its own README with setup and usage instructions.

## How the Pieces Fit Together

Two different relationships exist between these directories — a **runtime dependency**
and an **experiment-produces-asset** relationship. They are not the same thing:

- **`platform/backend` depends on `multi-agent-framework` at runtime.** The backend
  imports it as the `atlas_assistant` Python package (installed in editable mode from
  `multi-agent-framework/`, see [`platform/backend/README.md`](platform/backend/README.md)).
  `multi-agent-framework` is what actually runs the four conversational agents (paper
  interpretation, neuron selection, brain visualization, textual summarization) that
  `platform/backend` exposes over HTTP to `platform/frontend`.
- **`rag-evaluation` and `function-calling` are standalone experiment code, not runtime
  dependencies.** They are used once, offline, to *produce* the assets that
  `multi-agent-framework` consumes at runtime:
  - `rag-evaluation` benchmarks the RAG pipeline (retrieval + generation) used by the
    paper interpretation agent, and documents how to build the same HippoRAG2 knowledge
    base that `multi-agent-framework` loads at startup (see
    [`multi-agent-framework/readme.md`](multi-agent-framework/readme.md#data)).
  - `function-calling` trains and evaluates the fine-tuned model used by the neuron
    selection and brain visualization agents; the resulting model weights (see
    [`function-calling/README.md`](function-calling/README.md#fine-tuned-model-weights))
    are what `multi-agent-framework` calls out to via `FUNCTION_CALLING_MODEL` in its
    `.env`.

In short: to run the ProjAtlas platform, you need `platform/` + `multi-agent-framework/`
(plus a RAG index and a deployed fine-tuned model, built using the other two
directories). To reproduce the paper's reported numbers, `rag-evaluation` and
`function-calling` are self-contained and don't require the platform to be running.

## License

Code in this repository is licensed under [Apache License 2.0](LICENSE). See
[NOTICE](NOTICE) for third-party acknowledgements and licensing terms that apply to
model weights distributed alongside this repository (which are **not** covered by the
Apache-2.0 license).

## Citation

Citation will be added upon publication.
