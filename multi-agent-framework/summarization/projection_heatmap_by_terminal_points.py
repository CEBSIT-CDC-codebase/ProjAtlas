def projection_heatmap_by_terminal_points(data: dict) -> str:
    """
    Generate a prompt for analyzing neuron terminal point projections.

    Args:
        data (dict): Outer keys are target brain regions; inner keys are source brain regions;
                     values are integer terminal point counts.

    Returns:
        str: Formatted prompt string
    """
    return """Summarize only patterns directly supported by the provided data. Do not infer biological function, causality, cytoarchitecture, laminar organization, or circuit mechanisms unless such information is explicitly included in the input. If a requested analysis cannot be performed because required fields are missing, state this explicitly. Use brain region names exactly as they appear in the input data. Do not substitute, expand, or infer region names beyond what is provided.

You are a neuroscience data analyst. You will be given a JSON object describing terminal point-weighted projections between brain regions.

Data format:
- Outer keys: source brain regions (soma-containing regions)
- Inner keys: target brain regions receiving axonal terminals
- Values: number of axonal terminal points from the source region to each target region (integer counts)

Data:
{data}

Please provide a structured analysis covering:
1. **Top target regions**: Identify the target regions with the highest total terminal point counts summed across all source regions, reporting exact values.
2. **Source-specific innervation patterns**: For each source region, identify its primary targets and their terminal counts relative to other targets of that source.
3. **Dominant source-target pairs**: Highlight pairs with counts numerically largest, especially those clearly exceeding the remaining values in the same row or column.
4. **Cross-source convergence**: Identify target regions receiving high terminal counts from multiple source regions, as indicated by the provided data.
5. **Zero or near-zero projections**: Note source-target pairs with counts of zero or numerically negligible relative to other entries.

Format the response as concise bullet points under each numbered section. Use region names exactly as provided in the input data.""".format(data=data)
