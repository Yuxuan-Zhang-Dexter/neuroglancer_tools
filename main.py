import yaml
import sys
import os

# Import tasks from convert_tool and visualize_tool
from convert_tool import convert2h5
from visualize_tool import neuroglancer_tool

def load_config():
    # Load configuration from YAML file
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    return config

def main():
    # Load configuration
    config = load_config()

    # Determine the task to run
    task = config.get('task')
    if task == 'visualize':
        print('Running visualization task.')
        neuroglancer_tool.run_visualization(config['visualize'])
    elif task == 'convert':
        print('Running conversion task.')
        convert2h5.run_conversion(config['convert'])
    else:
        raise ValueError(f"Unknown task: {task}. Please choose 'visualize' or 'convert'.")

if __name__ == '__main__':
    main()
