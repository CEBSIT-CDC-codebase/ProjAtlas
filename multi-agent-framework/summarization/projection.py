def generate_projection_prompt(data: list[dict]) -> str:
    """
    Generate a prompt for summarizing neural projection information to brain regions.
    Args:
        data: List of dicts with fields (name, leftLength, rightLength) for axon length data,
              or (name, count) for neuron count data.
    Returns:
        str: Generated prompt text
    """
    has_length = len(data) > 0 and "leftLength" in data[0]

    base_prompt = """Summarize only patterns directly supported by the provided data. Do not infer biological function, causality, cytoarchitecture, laminar organization, or circuit mechanisms unless such information is explicitly included in the input. If a requested analysis cannot be performed because required fields are missing, state this explicitly. Use brain region names exactly as they appear in the input data. Do not substitute, expand, or infer region names beyond what is provided.

You are a neuroscience data analyst. You will be given a list of brain regions with associated projection metrics. """

    if has_length:
        prompt = base_prompt + """Each record contains a brain region name with left and right hemisphere axon lengths in micrometers (fields: name, leftLength, rightLength).

Data:
{data}

Please provide a structured summary covering:
1. **Top projection regions**: List the target regions with the numerically largest total axon length (leftLength + rightLength), reporting exact values.
2. **Hemispheric asymmetry**: For each region, compare leftLength and rightLength; note regions where one hemisphere value clearly exceeds the other based on the provided values.
3. **Distribution breadth**: Describe whether axon length concentrates in a small number of regions or distributes broadly, based on the provided values.
4. **Sparse projections**: Note regions with values numerically close to zero relative to the top entries.
5. **Left vs. right discordance**: If left and right hemisphere rankings differ substantially, note the discordance.

Format the response as concise bullet points under each numbered section. Use region names exactly as provided in the input data."""
    else:
        prompt = base_prompt + """Each record contains a brain region name with the number of projecting neurons (fields: name, count).

Data:
{data}

Please provide a structured summary covering:
1. **Top projection regions**: List the target regions with the numerically highest neuron counts, reporting exact values.
2. **Distribution breadth**: Describe whether neuron counts concentrate in a small number of regions or distribute broadly, based on the provided values.
3. **Dominant regions**: Highlight regions with counts numerically largest, especially those clearly exceeding the remaining values.
4. **Sparse projections**: Note regions with counts numerically close to zero relative to the top entries.
5. **Hierarchical pattern**: If region names suggest a hierarchical relationship (e.g., parent and child regions both present), describe the count distribution across levels based solely on the provided names and values.

Format the response as concise bullet points under each numbered section. Use region names exactly as provided in the input data."""

    return prompt.format(data=data)
