# RAG Evaluation Data Pipeline

Part of the [ProjAtlas](../) code repository. Generates the evaluation dataset and
evaluates retrieval/generation quality for the paper interpretation agent's RAG system
(see paper Methods: "RAG benchmark and evaluation").

Core claim: **RAG outperforms no-RAG**.

## Pipeline Architecture

```
Step 1              Step 2                Step 3              Step 4                Step 5
Generate QA GT →    RAG retrieval    →    No-RAG          →    Judge + Recall   →    Vote
(per species)       + answer              baseline             (3 models            aggregation
                     (per species)         (per species)         in parallel)         (majority vote)
```

Data flow:

```
Paper Markdown ──→ generate_qa.py ──→ all_qa_{species}.json (Question + Ground Truth + Evidence)
                                          │
                    ┌─────────────────────┼──────────────────────────┐
                    ↓                     ↓                          ↓
    get_retrieved_chunks.py      generate_without_rag.py      generate_without_rag.py --model
    (HippoRAG2 retrieval          (ACTIVE_MODEL answers          (Qwen3 / Llama3.3
     + LLM answer)                 directly)                     answer directly)
                    ↓                     ↓                          ↓
    *_output_{species}_top10.json   without_rag_{species}.json  without_rag_{species}_{model}.json
                    │                     │                          │
                    ├──────────┬──────────┴──────────────────────────┘
                    │          ↓
                    │   judge_correctness.py (evaluates correctness + hallucination)
                    │   (evaluates both RAG and all Without-RAG answers)
                    │          ↓
                    │   results/judge/*_voted.json + judge_summary.txt
                    │
                    ↓
              recall_at_k.py (evaluates retrieval quality, RAG only)
              (whether ground truth evidence is among the top-10 chunks)
                    ↓
              results/recall/*_voted.json + recall_summary.txt
```

## Repository Structure

```
rag-evaluation/
├── scripts/
│   ├── generate_qa.py              # Step 1: generate QA + ground truth evidence from papers
│   ├── get_retrieved_chunks.py     # Step 2: HippoRAG2 top-10 retrieval + answer generation
│   ├── generate_without_rag.py     # Step 3: no-RAG baseline answers
│   └── test_api.py                 # Utility: verify API connectivity
├── eval/
│   ├── judge_correctness.py        # Multi-model voting judge (correctness + hallucination)
│   └── recall_at_k.py              # Multi-model voting Recall@10 (RAG only)
├── data/
│   ├── SOURCE_PAPERS.md            # Source paper list (DOI/citations); full text not
│   │                                # redistributed in this repo due to copyright
│   ├── RAG-md-docs/                # Platform user guide (not third-party copyrighted
│   │                                # content, redistributed with this repo)
│   ├── RAG-md-mouse/                # [you must provide] full text of 8 mouse papers,
│   │                                # see SOURCE_PAPERS.md
│   ├── RAG-md-macaque/              # [you must provide] full text of 3 macaque papers,
│   │                                # see SOURCE_PAPERS.md
│   ├── rag-mouse/                  # [auto-generated] HippoRAG2 offline index (mouse)
│   └── rag-macaque/                # [auto-generated] HippoRAG2 offline index (macaque)
├── output/                         # Generated QA data (included in this repository)
│   ├── all_qa_mouse.json
│   └── all_qa_macaque.json
├── results/                        # Evaluation results (included in this repository;
│                                   # correspond to paper Table 2 / Extended Data Table 2)
│   ├── get_retrieved_chunks_output_{species}_top10.json
│   ├── without_rag_{species}_{model}.json
│   ├── judge/                      # Multi-model voting results (correctness + hallucination)
│   │   ├── judge_{species}_{mode}_{gpt|claude|gemini}.json
│   │   ├── judge_{species}_{mode}_voted.json
│   │   ├── judge_{species}_{mode}_conflicts.json
│   │   └── judge_summary.txt
│   └── recall/                     # Multi-model voting results (Recall@10, RAG only)
│       ├── recall_{species}_{gpt|claude|gemini}.json
│       ├── recall_{species}_voted.json
│       ├── recall_{species}_conflicts.json
│       └── recall_summary.txt
├── .env.example
└── README.md
```

Full paper text (`data/RAG-md-mouse/`, `data/RAG-md-macaque/`) and the HippoRAG2 offline
indices generated from it (`data/rag-mouse/`, `data/rag-macaque/`) are not redistributed
with this repository due to copyright/size constraints. To reproduce the full pipeline,
first read [`data/SOURCE_PAPERS.md`](data/SOURCE_PAPERS.md) for the paper list and DOIs,
obtain the source papers yourself and convert them to Markdown, place them in the
corresponding directories, then run the scripts starting from Step 1 to generate the
index and evaluation results.

## Full CLI Usage

### Step 1: Generate QA Ground Truth

Generate single-evidence and multi-evidence QA pairs from paper Markdown.
Documents are dynamically split by size (no split under 30KB; 2 parts for 30–60KB; 3 parts
for 60–90KB; 4 parts for 90KB+), with 10 single-evidence and 8 multi-evidence pairs
generated per part. Supports resuming from checkpoints.

```bash
python scripts/generate_qa.py --species mouse
python scripts/generate_qa.py --species macaque
```

Output: `output/all_qa_mouse.json`, `output/all_qa_macaque.json`

### Step 2: RAG Retrieval + Answer Generation

Use HippoRAG2 to retrieve the top-10 chunks for each question and generate an answer with
an LLM. Mouse and macaque use different knowledge bases and must be run separately.

```bash
python scripts/get_retrieved_chunks.py --species mouse --top-k 10 output/all_qa_mouse.json
python scripts/get_retrieved_chunks.py --species macaque --top-k 10 output/all_qa_macaque.json
```

Output: `results/get_retrieved_chunks_output_mouse_top10.json`, `results/get_retrieved_chunks_output_macaque_top10.json`

### Step 3: No-RAG Baseline

Have the LLM answer the same questions directly, without retrieved context. Can run in
parallel with Step 2.

Four models are supported, together forming the benchmark: Mistral (same model as RAG,
for a fair comparison), DeepSeek, Qwen2.5-72B, Llama3.3.

```bash
# Mistral-Small-3.1-24B (local inference cluster, same model as RAG, for a fair comparison)
python scripts/generate_without_rag.py --species mouse --model mistral
python scripts/generate_without_rag.py --species macaque --model mistral

# DeepSeek-v4-pro
python scripts/generate_without_rag.py --species mouse --model deepseek
python scripts/generate_without_rag.py --species macaque --model deepseek

# Qwen2.5-72B (local inference cluster)
python scripts/generate_without_rag.py --species mouse --model qwen2.5
python scripts/generate_without_rag.py --species macaque --model qwen2.5

# Llama3.3 (local inference cluster)
python scripts/generate_without_rag.py --species mouse --model llama3.3
python scripts/generate_without_rag.py --species macaque --model llama3.3
```

Output:
- `results/without_rag_{species}_mistral.json` — Mistral-Small-3.1-24B
- `results/without_rag_{species}_deepseek.json` — DeepSeek-v4-pro
- `results/without_rag_{species}_qwen2.5.json` — Qwen2.5-72B
- `results/without_rag_{species}_llama3.3.json` — Llama3.3

### Step 4: Judge Evaluation (3-model parallel voting)

3 judge models (GPT-5.4, Claude Sonnet 4, Gemini 3.1 Pro) evaluate the correctness and
hallucination of each answer in parallel. Each model writes its own output file
independently and supports resuming from checkpoints.

```bash
# Verify API connectivity
python scripts/test_api.py

# RAG
python eval/judge_correctness.py --species mouse --mode rag
python eval/judge_correctness.py --species macaque --mode rag

# No-RAG (Mistral baseline)
python eval/judge_correctness.py --species mouse --mode without_rag_mistral
python eval/judge_correctness.py --species macaque --mode without_rag_mistral

# No-RAG (DeepSeek baseline)
python eval/judge_correctness.py --species mouse --mode without_rag_deepseek
python eval/judge_correctness.py --species macaque --mode without_rag_deepseek

# No-RAG (Qwen2.5-72B baseline)
python eval/judge_correctness.py --species mouse --mode without_rag_qwen2.5
python eval/judge_correctness.py --species macaque --mode without_rag_qwen2.5

# No-RAG (Llama3.3 baseline)
python eval/judge_correctness.py --species mouse --mode without_rag_llama3.3
python eval/judge_correctness.py --species macaque --mode without_rag_llama3.3
```

### Step 4b: Recall@10 Evaluation (3-model parallel voting, RAG only)

Evaluates retrieval quality: whether the ground truth evidence is covered by the top-10
retrieved chunks. Uses the RAGAS Context Recall methodology, judged evidence by evidence.
**Evaluated for RAG results only** (no-RAG has no retrieval step, so recall cannot be
evaluated).

```bash
python eval/recall_at_k.py --species mouse
python eval/recall_at_k.py --species macaque
```

### Step 5: Vote Aggregation

Read all per-model results and produce final scores and a summary report by majority vote.

```bash
python eval/judge_correctness.py --vote
python eval/recall_at_k.py --vote
```

Output: `results/judge/judge_summary.txt`, `results/recall/recall_summary.txt`

## Evaluation Metrics

| Metric | Range | Description |
|------|------|------|
| Correctness | 0 / 0.5 / 1 | Factual accuracy and completeness of the answer relative to the ground truth |
| Hallucination | 0 / 1 | Whether the answer contains fabricated information (invented citations, data, etc.) |
| Recall@10 | 0–1 | Retrieval coverage (whether the ground truth evidence is among the top-10 chunks) |

## Voting Rules

- **Correctness**: majority vote (2:1 or 3:0). If all 3 values differ (one each of 0, 0.5, 1), flagged as a conflict requiring manual review.
- **Hallucination**: majority vote (only 0/1, so a 3-way split cannot occur).
- **Recall@10**: majority vote. If there is no unique majority (3-way split), flagged as a conflict requiring manual review.
- Correctness conflicts are written to `judge_{species}_{mode}_conflicts.json`; fill in the `resolved_correctness` field and re-run `--vote` to include them in the aggregate.
- Recall conflicts are written to `recall_{species}_conflicts.json`; fill in the `resolved_recall` field and re-run `--vote` to include them in the aggregate.

## Environment Setup

```bash
cp .env.example .env
```

The judge uses 3 sets of model configurations (all OpenAI-compatible):
- `OPENAI_*` — GPT-5.4
- `ANTHROPIC_*` — Claude Sonnet 4
- `GEMINI_*` — Gemini 3.1 Pro

Data generation uses the model specified by `ACTIVE_MODEL` (default: DeepSeek).

The Qwen2.5-72B / Llama3.3 models used for the without-RAG baseline are served by any
OpenAI-compatible local inference service (e.g. a self-hosted Ollama/vLLM instance),
configured via `CLUSTER_BASE_URL`:
- `CLUSTER_BASE_URL` — local inference service address
- `QWEN2_5_MODEL` — Qwen2.5-72B
- `LLAMA33_MODEL` — Llama3.3

## Dependencies

```bash
pip install openai python-dotenv
# hipporag2 is only needed for Step 2
```

## Citation

See the [repository root README](../README.md#citation) for the current citation.
