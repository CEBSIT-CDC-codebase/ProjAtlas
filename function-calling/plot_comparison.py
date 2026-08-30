#!/usr/bin/env python
"""
Generate comparison bar charts for function-calling accuracy across all models.
Produces two SVG figures:
  - Neuron Selection (Mouse + Macaque combined)
  - Brain Visualization (Neuroviz)
"""

import json
import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# Use Arial if available, otherwise fall back to DejaVu Sans
_arial_available = any('arial' in f.name.lower() for f in fm.fontManager.ttflist)
plt.rcParams['font.family'] = 'Arial' if _arial_available else 'DejaVu Sans'
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42
_font = 'Arial' if _arial_available else 'DejaVu Sans'

# ============================================================
# Configuration
# ============================================================

RESULTS_DIR = "results"
OUTPUT_DIR = "figures"

# Models to include (label, metrics_file)
MODELS = [
    ("xLAM-8B (Base)", "xlam_8b_base_metrics.json"),
    ("xLAM-8B (Fine-tuned)", "xlam_8b_finetuned_metrics.json"),
    ("GPT", "openai_gpt-5.4_unified_metrics.json"),
    ("Claude", "anthropic_claude-sonnet-4-6_unified_metrics.json"),
    ("Gemini", "google_gemini-3-pro-preview_unified_metrics.json"),
    ("Qwen", "qwen_qwen2.5-72b_unified_metrics.json"),
    ("Llama", "llama_llama3.3_unified_metrics.json"),
]

# Color palette — journal-friendly colors
COLORS = [
    "#D4A5D8",  # light purple - xLAM-8B Base
    "#E85D75",  # deep rose    - xLAM-8B Fine-tuned
    "#9B9FE8",  # light purple-blue - GPT
    "#4A5899",  # deep blue    - Claude
    "#5B8FE8",  # blue         - Gemini
    "#3B9B9B",  # deep cyan    - Qwen
    "#6EC6E6",  # sky blue     - Llama
]

# ============================================================
# Data loading
# ============================================================

def load_metrics(filename):
    filepath = os.path.join(RESULTS_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found, skipping")
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)["results"]


def combine_neuron_selection(data, task):
    """Combine Mouse + Macaque accuracy for a given task type."""
    mouse_key = f"Mouse_{task}"
    macaque_key = f"Macaque_{task}"
    combined_correct = data[mouse_key]["correct"] + data[macaque_key]["correct"]
    combined_total = data[mouse_key]["total"] + data[macaque_key]["total"]
    return (combined_correct / combined_total * 100) if combined_total > 0 else 0


def get_neuroviz_accuracy(data, task):
    """Get Neuroviz accuracy for a given task type."""
    return data[f"Neuroviz_{task}"]["accuracy"] * 100


# ============================================================
# Plotting
# ============================================================

def create_chart(title, model_labels, model_accuracies, colors, output_filename, show_legend=True):
    """Create a grouped bar chart comparing models across Zero/Single/Parallel."""
    tasks = ['Zero', 'Single', 'Parallel']
    n_models = len(model_labels)

    # No gap between bars within a group; small gap between groups
    width = 0.10
    group_width = n_models * width          # bars touch each other (no intra-group gap)
    group_gap = 0.20                        # gap between groups (~2 bar widths)
    x = np.arange(len(tasks)) * (group_width + group_gap)
    offsets = np.linspace(-(n_models - 1) / 2, (n_models - 1) / 2, n_models) * width

    # 80 mm wide, keep original aspect ratio (~10:5.5 ≈ 1.818), so height ≈ 44 mm
    fig_w_in = 80 / 25.4
    fig_h_in = fig_w_in / (10 / 7.5)
    fig, ax = plt.subplots(figsize=(fig_w_in, fig_h_in))

    for i, (label, accs, color) in enumerate(zip(model_labels, model_accuracies, colors)):
        bars = ax.bar(x + offsets[i], accs, width, label=label, color=color,
                      edgecolor="white", linewidth=0.3, zorder=2)

        # Baseline tick for zero values
        for bar in bars:
            if bar.get_height() == 0:
                cx = bar.get_x() + bar.get_width() / 2
                tick_half = width * 0.4
                ax.plot([cx - tick_half, cx + tick_half], [0, 0],
                        color=color, linewidth=1.5, solid_capstyle='round', zorder=3)

    ax.set_ylabel('Accuracy (%)', fontsize=9, fontname=_font, labelpad=2)
    ax.set_xlabel('Task Type', fontsize=9, fontname=_font, labelpad=2)
    ax.set_title(f'Function Calling Accuracy\nof {title} Agent',
                 fontsize=9, pad=4, fontname=_font)

    ax.set_xticks(x)
    ax.set_xticklabels(tasks, fontsize=7.5, fontname=_font)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.tick_params(axis='y', labelsize=7.5, pad=1)
    ax.tick_params(axis='x', pad=1)
    for lbl in ax.get_yticklabels():
        lbl.set_fontname(_font)
    ax.set_ylim(0, 115)

    if show_legend:
        ax.legend(fontsize=6.5, loc='upper center', bbox_to_anchor=(0.5, -0.28),
                  ncol=4, framealpha=0.8, columnspacing=0.8, handlelength=0.8,
                  handletextpad=0.4, borderpad=0.4,
                  prop={'family': _font, 'size': 6.5})
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Left margin: half a bar-width gap from y-axis; right margin: same
    half_bar = width / 2
    total_span = x[-1] + group_width / 2
    ax.set_xlim(x[0] - group_width / 2 - half_bar, total_span + half_bar)

    plt.tight_layout(pad=0.3)
    plt.savefig(output_filename, format='svg', bbox_inches='tight')
    print(f"Saved: {output_filename}")
    plt.close()


# ============================================================
# Main
# ============================================================

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load all model data
    model_labels = []
    model_data = []
    colors_used = []

    for i, (label, filename) in enumerate(MODELS):
        data = load_metrics(filename)
        if data is not None:
            model_labels.append(label)
            model_data.append(data)
            colors_used.append(COLORS[i])

    if not model_data:
        print("No metrics files found. Run evaluations first.")
        return

    # Neuron Selection (Mouse + Macaque)
    print("Generating Neuron Selection chart...")
    neuron_accs = []
    for data in model_data:
        neuron_accs.append([
            combine_neuron_selection(data, "Zero"),
            combine_neuron_selection(data, "Single"),
            combine_neuron_selection(data, "Parallel"),
        ])
    create_chart("Neuron Selection", model_labels, neuron_accs, colors_used,
                 os.path.join(OUTPUT_DIR, "fc_neuron_selection.svg"), show_legend=True)

    # Brain Visualization (Neuroviz)
    print("Generating Brain Visualization chart...")
    brain_accs = []
    for data in model_data:
        brain_accs.append([
            get_neuroviz_accuracy(data, "Zero"),
            get_neuroviz_accuracy(data, "Single"),
            get_neuroviz_accuracy(data, "Parallel"),
        ])
    create_chart("Brain Visualization", model_labels, brain_accs, colors_used,
                 os.path.join(OUTPUT_DIR, "fc_brain_visualization.svg"), show_legend=True)

    print("\nAll charts generated successfully!")


if __name__ == "__main__":
    main()
