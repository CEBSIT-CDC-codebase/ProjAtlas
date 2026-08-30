import json
from os.path import join, dirname

# REGIONS = json.load(open(join(dirname(__file__), 'regions.json')))
REGIONS = json.loads("[]")
TYPES = json.loads("[]")

def get_form_functions():
    return [
    {
        "type": "function",
        "function": {
            "name": "query_neurons_by_structure",
            "description": "Query neurons by structure, such as axon and dendrite or axon only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "axon_and_dendrite": {
                        "type": "boolean",
                        "description": "query neurons with 'axon and dendrite'.",
                    },
                    "axon_only": {
                        "type": "boolean",
                        "description": "query neurons with 'axon only'.",
                    },
                },
                "required": ["axon_and_dendrite", "axon_only"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "filter_neurons_by_hemisphere",
            "description": "Query the hemisphere location (left, right, or both) of the neurons in macaque brains.",
            "parameters": {
                "type": "object",
                "properties": {
                    "left": {
                        "type": "boolean",
                        "description": "Filter neurons with soma located in the left hemisphere.",
                    },
                    "right": {
                        "type": "boolean",
                        "description": "Filter neurons with soma located in the right hemisphere.",
                    },
                },
                "required": ["left", "right"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_axon_projects_to_location",
            "description": "Filter neurons based on their axon projections to specific brain regions. This helps identify neurons that send outputs to the selected target area.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "enum": REGIONS,
                        "description": 'brain region area.',
                    },
                },
                "required": ["region"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_soma_location",
            "description": "Filter neurons based on their soma location in a specific brain region. This helps narrow down neurons to those with cell bodies in the selected area.",
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "enum": REGIONS,
                        "description": 'brain region area.',
                    },
                },
                "required": ["region"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_neuron_type",
            "description": "Set morphological neuron type for filtering.",
            "parameters": {
                "type": "object",
                "properties": {
                    "neuron_type": {
                        "type": "string",
                        "enum": TYPES,
                        "description": 'neuron type names.',
                    },
                },
                "required": ["neuron_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_to_scene",
            "description": "Add neurons to the scene.",
            "parameters": {
                "type": "object",
                "properties": {
                    "add": {
                        "type": "boolean",
                        "description": "A boolean flag. Set to True to add the neurons to the scene.",
                    },
                },
                "required": ["add"],
            },
        },
    },
]