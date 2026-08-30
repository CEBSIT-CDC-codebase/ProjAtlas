def projection_heatmap_by_axon_length(data: dict) -> str:
    """
    Generate a prompt for analyzing neuron axon length projections.

    Args:
        data (dict): Outer keys are target brain regions; inner keys are source brain regions;
                     values are total axon length in micrometers (float).

    Returns:
        str: Formatted prompt string
    """
    return """Summarize only patterns directly supported by the provided data. Do not infer biological function, causality, cytoarchitecture, laminar organization, or circuit mechanisms unless such information is explicitly included in the input. If a requested analysis cannot be performed because required fields are missing, state this explicitly. Use brain region names exactly as they appear in the input data. Do not substitute, expand, or infer region names beyond what is provided.

You are a neuroscience data analyst. You will be given a JSON object describing axon length-weighted projections between brain regions.

Data format:
- Outer keys: source brain regions (soma-containing regions)
- Inner keys: target brain regions receiving axonal projections
- Values: total axon length (micrometers) from the source region to each target region

Data:
{data}

Please provide a structured analysis covering:
1. **Top target regions**: Identify the target regions with the highest total incoming axon length summed across all source regions, reporting exact values.
2. **Source-specific patterns**: For each source region, identify its dominant target regions and their axon lengths relative to other targets of that source.
3. **Dominant source-target pairs**: Highlight pairs with values numerically largest, especially those clearly exceeding the remaining values in the same row or column.
4. **Apparent source clusters**: Identify apparent groups of source regions with similar high-ranking targets, if evident from the provided values.
5. **Sparse projections**: Note source-target pairs with values of zero or numerically close to zero relative to other entries.

Format the response as concise bullet points under each numbered section. Use region names exactly as provided in the input data.""".format(data=data)
