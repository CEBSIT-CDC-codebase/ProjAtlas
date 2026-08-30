def generate_viewport_summary_prompt(neurons, regions):
    """
    Generate a prompt for summarizing neuron types and region names in the viewport.

    Args:
        neurons: List containing neuron type information
        regions: List containing region names

    Returns:
        str: Generated prompt text
    """
    prompt = f"""Please summarize the following information about neurons and brain regions in the current viewport:

Neuron Types:
{format_neuron_types(neurons)}

Brain Regions:
{format_region_names(regions)}

Provide a concise summary that includes:
1. The main types of neurons present
2. The key brain regions visible
3. Any notable relationships between neuron types and regions
"""
    print("Generated Viewport Summary Prompt:\n", prompt)
    return prompt

def format_neuron_types(neurons):
    """Format neuron type information."""
    if not neurons:
        return "No neurons present in viewport"
    
    neuron_types = {n['type_name'] for n in neurons if 'type_name' in n}
    return "\n".join(f"- {ntype}" for ntype in sorted(neuron_types))

def format_region_names(regions):
    """Format region name information."""
    if not regions:
        return "No brain regions present in viewport"
    
    region_names = {r['name'] for r in regions if 'name' in r}
    return "\n".join(f"- {name}" for name in sorted(region_names))
