import os
import numpy as np
from PIL import Image, ImageFile
import h5py
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import gc

# Configure PIL to handle large and truncated images
Image.MAX_IMAGE_PIXELS = None
ImageFile.LOAD_TRUNCATED_IMAGES = True

def combine_images_to_hdf5(input_dir, output_file, dataset_name, chunk_size=10):
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_files = [f for f in sorted(os.listdir(input_dir)) if f.lower().endswith(('png', 'tiff', 'tif'))]
    total_images = len(image_files)
    if total_images == 0:
        print(f"No images found in {input_dir}.")
        return

    # Initialize HDF5 file
    with h5py.File(output_file, 'w') as h5file:
        for chunk_index in tqdm(range(0, total_images, chunk_size), desc="Processing chunks", unit="file"):
            chunk_files = image_files[chunk_index:chunk_index + chunk_size]
            images = []

            for file_name in tqdm(chunk_files, desc="Processing files", leave=False):
                file_path = os.path.join(input_dir, file_name)
                try:
                    with Image.open(file_path) as img:
                        if file_name.lower().endswith(('tiff', 'tif')) and img.n_frames > 1:
                            print(f"Skipping multi-frame TIFF file: {file_name}")
                            continue
                        img_array = np.array(img)
                        images.append(img_array)
                except Exception as e:
                    print(f"Failed to process image {file_name}: {e}")
                    continue

            if chunk_index == 0:
                # Create dataset with the shape of the first image
                h5file.create_dataset(dataset_name, data=images, maxshape=(None,) + images[0].shape, compression="gzip")
            else:
                # Resize the dataset to accommodate new data
                h5file[dataset_name].resize((h5file[dataset_name].shape[0] + len(images)), axis=0)
                h5file[dataset_name][-len(images):] = images

            del images
            gc.collect()

    print(f"Combined images into {output_file}")

def process_images(pair):
    input_dir, output_file, dataset_name = pair
    combine_images_to_hdf5(input_dir, output_file, dataset_name)

def check_file_completeness(image_dir, output_file, dataset_name):
    images_num = len(os.listdir(image_dir))
    with h5py.File(output_file, 'r') as fl:
        tmp_dataset = fl[dataset_name]
        h5_num = tmp_dataset.shape[0]
    return images_num == h5_num

def run_conversion(config):
    input_output_pairs = [
        (config['directories']['raw_image_dir'], config['output_files']['raw_output_file'], 'raw_images'),
        (config['directories']['segmentation_dir'], config['output_files']['seg_output_file'], 'seg_images')
    ]

    # Compress and convert images files into h5 files
    if not (check_file_completeness(*input_output_pairs[0]) and check_file_completeness(*input_output_pairs[1])):
        try:
            os.remove(config['output_files']['raw_output_file'])
            os.remove(config['output_files']['seg_output_file'])
        except FileNotFoundError:
            pass
        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.map(lambda p: process_images(p), input_output_pairs)
