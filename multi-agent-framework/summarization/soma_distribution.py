def generate_soma_distribution_prompt(region_data) -> str:
    """
    Generate a prompt for summarizing neuronal soma distribution across brain regions.
    Args:
        region_data: List of dicts with fields (name, soma_count). No volume data is provided.
    Returns:
        Formatted prompt string
    """
    prompt = """Summarize only patterns directly supported by the provided data. Do not infer biological function, causality, cytoarchitecture, laminar organization, or circuit mechanisms unless such information is explicitly included in the input. If a requested analysis cannot be performed because required fields are missing, state this explicitly. Use brain region names exactly as they appear in the input data. Do not substitute, expand, or infer region names beyond what is provided.

You are a neuroscience data analyst. You will be given a list of brain regions with soma counts. Each record contains a brain region name and the number of neuronal cell bodies (somas) located in that region (fields: name, soma_count). No regional volume data is provided; report soma counts or relative proportions only, not density.

Data:
{data}

Please provide a structured summary covering:
1. **Regions with highest soma counts**: Identify the regions with the numerically largest soma_count values, reporting exact counts.
2. **Relative distribution**: Describe the proportion of somas in each region relative to the total count across all provided regions.
3. **Inter-regional comparison**: Compare soma counts across regions; highlight values numerically largest or smallest, especially those clearly exceeding or falling below the remaining values.
4. **Hierarchical pattern**: If region names suggest a hierarchical relationship (e.g., parent and child regions both present), describe the count distribution across levels based solely on the provided names and values.
5. **Spatial context**: Note anatomical axis context (anterior-posterior, medial-lateral, dorsal-ventral) only if coordinate or axis data is explicitly provided; otherwise state this analysis cannot be performed.

Format the response as concise bullet points under each numbered section. Use region names exactly as provided in the input data.""".format(data=region_data)

    return prompt
