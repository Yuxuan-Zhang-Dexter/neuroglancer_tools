from PIL import Image
from PIL import ImageFile
import numpy as np
import os
import neuroglancer
import numpy as np
import imageio
import h5py
from cloudvolume import CloudVolume
from tqdm import tqdm
import gc
import webbrowser
import tempfile

class basic_functions:
    def __init__(self, viewer, gt, res):
        self.viewer = viewer
        self.gt = gt
        self.res = res
        self.seg_ids = np.unique(gt)
        
        # - add actions
        self.viewer.actions.add("mouse_coordinate", self.mouse_coordinate)
        self.viewer.actions.add("generate_all_meshes", self.generate_all_meshes)
        
        # - add info
        with self.viewer.config_state.txn() as s:

            s.input_event_bindings.viewer['keyt'] = 'mouse_coordinate'
            s.status_messages['mouse_info'] = "press t to check mouse location info"
            
            s.input_event_bindings.viewer['control+shift+keyg'] = 'generate_all_meshes'

    # - Show mouse voxel and selected layer value
    def mouse_coordinate(self, s):
        with self.viewer.config_state.txn() as st:
            st.status_messages['mouse_info'] = ('mouse position = %r selected value = %s') % (s.mouse_voxel_coordinates, s.selected_values)

    # - Generate all meshes
    def generate_all_meshes(self, s):
        with self.viewer.config_state.txn() as st:
            st.status_messages['generate_meshes'] = "Start Generating All Meshes"
        with self.viewer.txn() as s:
            for id in self.seg_ids:
                s.layers['segmentation'].segments.add(id)
        with self.viewer.config_state.txn() as st:
            st.status_messages['generate_meshes'] = "Finish Generating All Meshes"


    # - Screenshot meshes....