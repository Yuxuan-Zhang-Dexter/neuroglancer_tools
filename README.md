
# Neuroglancer Visualization and Image Conversion Tools


## Overview


This repository contains tools for visualizing neuroimaging data using Neuroglancer and for converting image datasets into HDF5 format. The tools are configurable via a YAML file, making it easy to switch between tasks such as visualization and conversion.


## Directory Structure


```plaintext
root_directory/
│
├── main.py                  # Entry point to run tasks based on the YAML configuration
├── config.yaml              # Configuration file for specifying task details
├── convert_tool/            # Contains tools for converting images
│   └── convert2h5.py        # Script for image conversion to HDF5 format
└── visualize_tool/          # Contains tools for visualizing data with Neuroglancer
    ├── neuroglancer_tool.py # Script for Neuroglancer visualization
    ├── basic_tools.py       # Contains basic functions for visualization
    └── merge_split_tool.py  # Contains functions for merging and splitting data layers
```


## Prerequisites


- Python 3.x
- Install dependencies by running:


  ```bash
  pip install -r requirements.txt
  ```


## Configuration


The program is configured using the `config.yaml` file. This file allows you to specify parameters for different tasks such as visualization with Neuroglancer or image conversion to HDF5.


### Example `config.yaml`


```yaml
task: "visualize"  # or "convert"


visualize:
  directories:
    raw_image_dir: "/media/mitochondria/Elements/spineheads/raw_images"
    segmentation_dir: "/media/mitochondria/Elements/spineheads/segmentations"
  output_files:
    raw_output_file: "/home/mitochondria/Desktop/yuxuan_exp/developing_neuroglancer_tools/dataset/raw_images_h5/all_raw_images.h5"
    seg_output_file: "/home/mitochondria/Desktop/yuxuan_exp/developing_neuroglancer_tools/dataset/seg_images_h5/all_seg_images.h5"
  neuroglancer:
    start_port: 8000
    end_port: 9000
    ip_address: "localhost"
  visualization:
    num_images: 5
    scales: [60, 4, 4]
    units: ["nm", "nm", "nm"]


convert:
  directories:
    raw_image_dir: "/media/mitochondria/Elements/spineheads/raw_images"
    segmentation_dir: "/media/mitochondria/Elements/spineheads/segmentations"
  output_files:
    raw_output_file: "/home/mitochondria/Desktop/yuxuan_exp/developing_neuroglancer_tools/dataset/raw_images_h5/all_raw_images.h5"
    seg_output_file: "/home/mitochondria/Desktop/yuxuan_exp/developing_neuroglancer_tools/dataset/seg_images_h5/all_seg_images.h5"
```


### Configuration Details


- **task**: Specifies which task to run. Options are `visualize` or `convert`.
- **visualize**: Configuration for the Neuroglancer visualization task.
  - **directories**: Directories for raw images and segmentations.
  - **output_files**: HDF5 output file paths.
  - **neuroglancer**: Neuroglancer server settings such as IP address and port range.
  - **visualization**: Number of images to visualize and scale settings.
- **convert**: Configuration for the image conversion task.
  - **directories**: Directories for input images and output HDF5 files.
  - **output_files**: HDF5 output file paths.


## Usage


### Running the Program


To run the program, use the `main.py` script. The task executed will depend on the configuration specified in the `config.yaml` file.


1. **Visualize with Neuroglancer:**


   Ensure your `config.yaml` is set to the `visualize` task:
   
   ```yaml
   task: "visualize"
   ```


   Then, run:


   ```bash
   python main.py
   ```


2. **Convert Images to HDF5:**


   Set the `config.yaml` to the `convert` task:
   
   ```yaml
   task: "convert"
   ```


   Then, run:


   ```bash
   python main.py
   ```


### Customizing the Configuration


You can easily switch between different configurations by modifying the `config.yaml` file. Adjust the paths, number of images, and other settings as per your requirements.


## Neuroglancer Key Bindings


The `visualize_tool` also includes several custom keyboard bindings for interacting with Neuroglancer's viewer. Below is an overview of the key bindings and their functions:


### **`basic_functions` Class:**


| Key Binding                  | Functionality                                | Method in Class                  |
|------------------------------|----------------------------------------------|----------------------------------|
| `t`                          | Show mouse coordinates and selected values  | `mouse_coordinate` in `basic_functions` |
| `Ctrl + Shift + G`           | Generate all 3D meshes for segmentation IDs  | `generate_all_meshes` in `basic_functions` |
| `Ctrl + Shift + H`           | Save viewer state to HDF5 and JSON files    | `save_h5_state` in `basic_functions` |


### **`merge_split_function` Class:**


| Key Binding                  | Functionality                                | Method in Class                  |
|------------------------------|----------------------------------------------|----------------------------------|
| `Shift + Q`                  | Add an annotation at the current position   | `add_annotation` in `merge_split_function` |
| `Ctrl + Shift + M`           | Merge two annotated segments                | `merge_segments` in `merge_split_function` |
| `Ctrl + Shift + S`           | Split a segment into two at annotation points | `split_segments` in `merge_split_function` |


### Explanation:


- **Adding Annotations:** Annotations are crucial for defining regions to be merged or split. These act as markers for operations.
- **Merging Segments:** Merge incorrectly separated segments into one. This allows you to correct over-segmentation.
- **Splitting Segments:** Split a segment into two, particularly when two distinct objects are mistakenly grouped into one segment.


## Additional Information


### Error Handling


- Ensure that the directories specified in `config.yaml` exist and contain the required files.
- Make sure that all necessary Python dependencies are installed as specified in `requirements.txt`.


### Further Development


This toolset is designed to be modular and extensible. Feel free to add additional tasks or customize existing ones as per your project’s needs.


## License
