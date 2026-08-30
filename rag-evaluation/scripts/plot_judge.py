"""
Plot Correctness + Hallucination comparison (RAG vs w/o RAG).
Generates a grouped bar chart for Fig.2b.

X-axis: metrics (Correctness, Hallucination Rate)
Legend: RAG (green) vs w/o RAG (purple)

Usage:
  python scripts/plot_judge.py
  python scripts/plot_judge.py --output figures/fig2b.pdf
"""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# Use Arial if available, otherwise fall back to DejaVu Sans
_arial_available = any('arial' in f.name.lower() for f in fm.fontManager.ttflist)
plt.rcParams['font.family'] = 'Arial' if _arial_available else 'DejaVu Sans'
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

ROOT_DIR = Path(__file__).parent.parent
JUDGE_DIR = ROOT_DIR / "results" / "judge"

# Colors per mode
MODE_STYLES = {
    "rag":                  {"color": "#8F8DC4", "label": "RAG (Mistral)"},   # deep rose - med_OFC
    "without_rag_mistral":  {"color": "#F29091", "label": "Mistral"},          # light purple-blue - dlPFC
    "without_rag_deepseek": {"color": "#D4A5D8", "label": "DeepSeek"},         # light purple - M1/PM
    "without_rag_qwen2.5":  {"color": "#5B8FE8", "label": "Qwen"},             # blue - PMd
    "without_rag_llama3.3": {"color": "#4A5899", "label": "Llama"},            # deep blue - vlPFC
}
MODE_ORDER = ["rag", "without_rag_mistral", "without_rag_deepseek", "without_rag_qwen2.5", "without_rag_llama3.3"]


def load_metrics():
    """Load voted results and compute overall correctness & hallucination rate."""
    metrics = {}  # mode -> {"correctness": float, "hallucination": float}

    for mode in MODE_ORDER:
        all_c = []
        all_h = []
        for species in ("mouse", "macaque"):
            voted_file = JUDGE_DIR / f"judge_{species}_{mode}_voted.json"
            if not voted_file.exists():
                continue
            data = json.loads(voted_file.read_text(encoding="utf-8"))
            for v in data:
                if v["correctness"] is not None:
                    all_c.append(v["correctness"])
                if v["hallucination"] is not None:
                    all_h.append(v["hallucination"])

        if all_c and all_h:
            metrics[mode] = {
                "correctness": sum(all_c) / len(all_c),
                "hallucination": sum(1 for h in all_h if h == 1) / len(all_h),
            }

    return metrics


def plot(metrics, output_path):
    """Generate grouped bar chart."""
    present_modes = [m for m in MODE_ORDER if m in metrics]
    n = len(present_modes)

    x_labels = ["Correctness", "Hallucination"]
    width = 0.06
    group_gap = 0.35
    x_centers = np.arange(len(x_labels)) * group_gap

    fig, ax = plt.subplots(figsize=(4.5, 3.5))

    offsets = np.linspace(-(n - 1) / 2, (n - 1) / 2, n) * width

    for mode, offset in zip(present_modes, offsets):
        style = MODE_STYLES[mode]
        vals = [metrics[mode]["correctness"] * 100,
                metrics[mode]["hallucination"] * 100]
        bars = ax.bar(x_centers + offset, vals, width,
                      label=style["label"], color=style["color"],
                      edgecolor="white", linewidth=0.5)
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 1.5,
                    f"{h:.1f}", ha="center", va="bottom", fontsize=6.5)

    ax.set_title("Answer Correctness and Hallucination\nwith and without RAG",
                 fontsize=9, fontfamily="Arial" if _arial_available else "DejaVu Sans",
                 pad=8)
    ax.set_ylabel("Percentage (%)", fontsize=9)
    ax.set_xticks(x_centers)
    ax.set_xticklabels(x_labels, fontsize=9)
    ax.set_xlim(x_centers[0] - group_gap / 2, x_centers[-1] + group_gap / 2)
    ax.set_ylim(0, 110)
    ax.legend(fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, 1.0),
              ncol=3, framealpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig(output_path, format="svg", bbox_inches="tight")
    print(f"Saved: {output_path}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Plot judge metrics (Fig.2b)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output file path (default: figures/fig2b_judge.pdf)")
    args = parser.parse_args()

    output_path = args.output
    if output_path is None:
        fig_dir = ROOT_DIR / "figures"
        fig_dir.mkdir(exist_ok=True)
        output_path = fig_dir / "rag_judge_metrics.svg"

    metrics = load_metrics()
    if "rag" not in metrics:
        print("Error: need at least RAG voted results.")
        return

    plot(metrics, output_path)


if __name__ == "__main__":
    main()
