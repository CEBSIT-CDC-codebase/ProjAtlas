import json
from os.path import join, dirname

def get_neuroviz_functions():
    return [
    {
        "type": "function",
        "function": {
            "name": "set_camera",
            "description": "set viewport camera position and look at.",
            "parameters": {
                "type": "object",
                "properties": {
                    "camera": {
                        "type": "string",
                        "enum": json.load(open(join(dirname(__file__), 'cameras.json'), 'r', encoding='utf-8')),
                        "description": 'which camera position should be.',
                    },
                },
                "required": ["camera"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_neuron_mirror_state",
            "description": "set neurons mirror state in viewport.",
            "parameters": {
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "enum": ["left", "right", ""],
                        "description": 'mirror state neurons in viewport to left or right or empty string to reset state.',
                    },
                },
                "required": ["state"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_brain_region_coloring_scheme",
            "description": "set brain region coloring scheme in viewport.",
            "parameters": {
                "type": "object",
                "properties": {
                    "scheme": {
                        "type": "string",
                        "enum": ["cebsit", "allen", "random"],
                        "description": 'coloring scheme should be.',
                    },
                },
                "required": ["scheme"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_neuron_coloring_scheme",
            "description": "set neuron coloring scheme in viewport.",
            "parameters": {
                "type": "object",
                "properties": {
                    "scheme": {
                        "type": "string",
                        "enum": ["random", "mouseLine", "region", "structure"],
                        "description": 'coloring scheme should be.',
                    },
                },
                "required": ["scheme"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_reference_planes",
            "description": "set reference planes' visibility in viewport.",
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["segmentation", "average_brain_imageing_map"],
                        "description": 'which type reference planes to load into viewport.',
                    },
                    "sagittal": {
                        "type": "boolean",
                        "description": 'whether to load sagittal reference plane into viewport.',
                    },
                    "horizontal": {
                        "type": "boolean",
                        "description": 'whether to load horizontal reference plane into viewport.',
                    },
                    "coronal": {
                        "type": "boolean",
                        "description": 'whether to load coronal reference plane into viewport.',
                    },
                },
                "required": ["type", "sagittal", "horizontal", "coronal"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "take a screenshot of viewport.",
            "parameters": {
                "type": "object",
                "properties": {
                    "do_it": {
                        "type": "boolean",
                        "description": 'whether to take a screenshot of viewport.',
                    },
                },
                "required": ["do_it"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "play_example_animation",
            "description": "whether to play example animation in viewport.",
            "parameters": {
                "type": "object",
                "properties": {
                    "do_it": {
                        "type": "boolean",
                        "description": 'whether to play example animation in viewport.',
                    },
                },
                "required": ["do_it"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_region_picking_mode",
            "description": "whether to enable region picking in viewport.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "boolean",
                        "description": 'whether to enable region picking in viewport.',
                    },
                },
                "required": ["mode"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_neuron_picking_mode",
            "description": "whether to enable neuron picking in viewport.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "boolean",
                        "description": 'whether to enable neuron picking in viewport.',
                    },
                },
                "required": ["mode"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_neuron_display_mode",
            "description": "whether to enable neuron backbone display in viewport.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "boolean",
                        "description": 'whether to enable neuron backbone display in viewport, default false.',
                    },
                },
                "required": ["mode"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_neuron_soma_radius_scale",
            "description": "set neuron soma radisu scale in viewport.",
            "parameters": {
                "type": "object",
                "properties": {
                    "scale": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 10,
                        "description": 'set neuron soma radisu scale in viewport, default 1.',
                    },
                },
                "required": ["scale"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_coordinate_axis_visibility",
            "description": "whether to show coordinate axis in viewport.",
            "parameters": {
                "type": "object",
                "properties": {
                    "visibility": {
                        "type": "boolean",
                        "description": 'whether to show coordinate axis in viewport, default true.',
                    },
                },
                "required": ["visibility"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_background_color",
            "description": "set background color of viewport.",
            "parameters": {
                "type": "object",
                "properties": {
                    "color": {
                        "type": "string",
                        "description": 'hex color string as background color of viewport, default #000000.',
                    },
                },
                "required": ["color"],
            },
        },
    },
    ]