import json
import os

def flatten_region_structure(data):
    flattened = []
    
    def process_node(node):
        # Skip if node is not a dictionary
        if not isinstance(node, dict):
            return
        
        # Process sub_type_array and uid_array
        current_node = {}
        current_node['name'] = node['name']
        current_node['count'] = node['count']
        current_node['leftLength'] = node['leftLength']
        current_node['rightLength'] = node['rightLength']
        
        if current_node and current_node['count'] > 0:
            flattened.append(current_node)
        
        # Process regionObj if it exists
        for child in node['children']:
            process_node(child)
        
    # Process each top-level item
    for item in data:
        process_node(item)
    
    return flattened

def main():
    # Read the input file
    with open(os.path.join(os.path.dirname(__file__), 'projection-overview.json'), 'r') as f:
        data = json.load(f)
    
    # Flatten the structure
    flattened_data = flatten_region_structure(data)
    
    # Write the output
    with open(os.path.join(os.path.dirname(__file__), 'projection-length.json'), 'w') as f:
        # Remove the count field from each element
        filtered_data = [{k: v for k, v in item.items() if k != 'count'} for item in flattened_data]
        json.dump(filtered_data, f, indent=2)

    with open(os.path.join(os.path.dirname(__file__), 'projection-count.json'), 'w') as f:
        filtered_data = [{k: v for k, v in item.items() if k not in ['leftLength', 'rightLength']} for item in flattened_data]
        json.dump(filtered_data, f, indent=2)
if __name__ == '__main__':
    main()