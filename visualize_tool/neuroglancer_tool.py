import os
import numpy as np
from PIL import Image, ImageFile
import neuroglancer
import h5py
from tqdm import tqdm
import gc
import socket
import time
import webbrowser
from .basic_tools import basic_functions  # Import relative to the module
from .merge_split_tool import merge_split_function
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

# Configure PIL to handle large and truncated images
Image.MAX_IMAGE_PIXELS = None
ImageFile.LOAD_TRUNCATED_IMAGES = True

def find_available_port(start_port=8000, end_port=9000):
    """Find an available port in the given range."""
    for port in range(start_port, end_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(('127.0.0.1', port))
            if result != 0:  # Port is available
                return port
    raise RuntimeError("No available port found in the given range")

def choose_first_n_images(file_path, dataset_name, n):
    with h5py.File(file_path, 'r') as fl:
        tmp_dataset = fl[dataset_name]
        images = []
        for i in range(n):
            images.append(tmp_dataset[i])
        if dataset_name == 'seg_images':
            return np.array(images, dtype=np.uint32)
        return np.array(images)

def run_visualization(config):
    n = config['visualization']['num_images']
    ip = config['neuroglancer']['ip_address']
    port = find_available_port(config['neuroglancer']['start_port'], config['neuroglancer']['end_port'])
    neuroglancer.set_server_bind_address(bind_address=ip, bind_port=port)
    viewer = neuroglancer.Viewer()

    res = neuroglancer.CoordinateSpace(
        names=['z', 'y', 'x'],
        units=config['visualization']['units'],
        scales=config['visualization']['scales']
    )

    print('Load raw image and segmentation.')
    try:
        im = choose_first_n_images(config['output_files']['raw_output_file'], 'raw_images', n)
        gt = choose_first_n_images(config['output_files']['seg_output_file'], 'seg_images', n)
    except FileNotFoundError as e:
        print(e)
        return

    print(im.shape, gt.shape)

    def ngLayer(data, res, oo=[0, 0, 0], tt='segmentation'):
        return neuroglancer.LocalVolume(data, dimensions=res, volume_type=tt, voxel_offset=oo)
    
    im_layer = ngLayer(im, res, tt="image")
    gt_layer = ngLayer(gt, res, tt='segmentation')

    with viewer.txn() as s:
        s.layers.append(name='im', layer=im_layer)
        s.layers.append(name='gt', layer=gt_layer)
    
    basic_functions(viewer, im, gt, res)
    merge_split_function(viewer, gt, res, gt_layer)

    print(viewer)

    webbrowser.open_new_tab(str(viewer))

    # Keep the script running
    try:
        while True:
            pass  # Keep the server running
    except KeyboardInterrupt:
        print("Server stopped by user.")
