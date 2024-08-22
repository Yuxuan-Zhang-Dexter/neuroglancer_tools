import argparse
import neuroglancer
import neuroglancer.cli
import h5py
import neuroglancer.random_token
import numpy as np
import socket



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
from scipy.ndimage import label, generate_binary_structure, find_objects, center_of_mass
from scipy.spatial.distance import euclidean
import cv2

class merge_split_function:
    def __init__(self, viewer, gt, res, gt_layer, min_size = 40):
        self.viewer = viewer
        self.gt = gt
        self.res = res
        self.annotation_points = []
        self.annotation_order = 0
        self.gt_layer = gt_layer
        self.max_id = np.max(gt)
        self.min_size = min_size



        # - Adding actions
        self.viewer.actions.add("add_annotation", self.add_annotation)
        self.viewer.actions.add("merge_segments", self.merge_segments)
        self.viewer.actions.add("split_segments", self.split_segments)

        # - Binding keys
        with self.viewer.config_state.txn() as s:
            s.input_event_bindings.viewer['shift+keyq'] = "add_annotation"
            s.status_messages['add annotation info'] = "press shift+keyq to select segmentation"
            s.input_event_bindings.viewer['control+shift+keym'] = "merge_segments"
            s.input_event_bindings.viewer['control+shift+keys'] = 'split_segments'
            s.status_messages['merge info'] = "press control+shift+m to merge segmentation"
            s.status_messages['split info'] = "press control+shift+s to split segmentation"
    
    def add_annotation(self, s):
        coordinates = s.mouse_voxel_coordinates
        segment_id = s.selected_values.get("gt").value

        with self.viewer.config_state.txn() as st:
            st.status_messages['annotation info'] = ('Selected segmentation: mouse position = %r selected value = %s' %
                                                (s.mouse_voxel_coordinates, s.selected_values.get("gt").value))

        self.annotation_points.append((coordinates, segment_id))
        print(f"Added annotation at {coordinates} with segment ID {segment_id}")

        if len(self.annotation_points) > 2:
            with self.viewer.config_state.txn() as st:
                st.status_messages['annotation info'] = (f'Too much annotation points. It will automatically delete all points.')
            print(f'Too much annotation points. It will automatically delete all points.')
            self.annotation_points = []

    def merge_segments(self, s):
        if len(self.annotation_points) == 2:
            with self.viewer.config_state.txn() as st:
                st.status_messages['merge info'] = ('Start merging')
            segments = set(annotation[1] for annotation in self.annotation_points)

            segment_ids = list(segments)
            target_segment_id = segment_ids[0]
            merge_segment_id = segment_ids[1]

            print(f"current merge segment id: {merge_segment_id}")
            with self.viewer.config_state.txn() as st:
                st.status_messages['merge info'] = f"current merge segment id: {merge_segment_id}"
            self.gt[self.gt == merge_segment_id] = target_segment_id
            self.gt_layer.invalidate()
            self.annotation_points = []
            with self.viewer.config_state.txn() as st:
                st.status_messages['merge info'] = ('Merging done!')
            print('Merging done!')


    def split_segments(self, s):
        if len(self.annotation_points) != 2:
            print("Error: Exactly two annotation points are required to perform a split. ")
            return 
        print(f"check coordinate: {self.annotation_points[0][0]}")
        if self.annotation_points[0][1] == self.annotation_points[1][1]:
            with self.viewer.config_state.txn() as st:
                st.status_messages['split info'] = f"Start splitting"
            segment_id = self.annotation_points[0][1]
            with self.viewer.config_state.txn() as st:
                st.status_messages['split info'] = f"current split segment id: {segment_id}"
            print(f"current split segment id: {segment_id}")
            mask = self.gt == segment_id
            
            # - check mouse id
            mouse_coord_1 = self.annotation_points[0][0]
            mouse_coord_2 = self.annotation_points[1][0]
            mouse_coord_2d_1 = np.round(mouse_coord_1[1:])
            mouse_coord_2d_2 = np.round(mouse_coord_2[1:])

            z_list = []
            non_zero_slices = []
        

            for i in range(mask.shape[0]):

                slice_2d = mask[i, :, :]

                if np.any(slice_2d > 0):
                    z_list.append(i)
                    non_zero_slices.append(slice_2d)


            # - split instance slice by slice
            # - set close to the first mouse coordiante, the segment id doesn't need to change
            for non_zero_slice, z_id in zip(non_zero_slices, z_list):
                # - filter out tiny points
                non_zero_slice = non_zero_slice.astype(np.uint8)
                nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(non_zero_slice, connectivity=8)
                filtered_slice = np.zeros_like(non_zero_slice)
                for label_id in range(1, nlabels):
                    area = stats[label_id, cv2.CC_STAT_AREA]
                    if area >= self.min_size:
                        filtered_slice[labels == label_id] = 1

                labeled_array, num_features = label(filtered_slice, structure=generate_binary_structure(2, 2))
                object_slices = find_objects(labeled_array)

                if num_features > 2:
                    print("there are more than two splitting items.")
                    return
                else:
                    reshape_labeled_array = labeled_array[np.newaxis, :, :]
                    if num_features == 1:
                        center_coordinate_1 = center_of_mass(labeled_array == 1)
                        distance_1 = euclidean(center_coordinate_1, mouse_coord_2d_1)
                        distance_2 = euclidean(center_coordinate_1, mouse_coord_2d_2)

                        if distance_1 > distance_2:
                            y_start, y_stop = object_slices[0][0].start, object_slices[0][0].stop
                            x_start, x_stop = object_slices[0][1].start, object_slices[0][1].stop
                            self.gt[z_id, y_start:y_stop, x_start:x_stop][reshape_labeled_array[0, y_start:y_stop, x_start:x_stop] == 1 ] = self.max_id + 1

                    elif num_features == 2:
                        center_coordinate_1 = center_of_mass(labeled_array == 1)
                        center_cooridnate_2 = center_of_mass(labeled_array == 2)
                        distance_mouse_1 = euclidean(center_coordinate_1, mouse_coord_2d_1)
                        distance_mouse_2 = euclidean(center_cooridnate_2, mouse_coord_2d_1)

                        if distance_mouse_1 > distance_mouse_2:
                            y_start, y_stop = object_slices[0][0].start, object_slices[0][0].stop
                            x_start, x_stop = object_slices[0][1].start, object_slices[0][1].stop
                            self.gt[z_id, y_start:y_stop, x_start:x_stop][reshape_labeled_array[0, y_start:y_stop, x_start:x_stop] == 1] = self.max_id + 1
                        else:
                            y_start, y_stop = object_slices[1][0].start, object_slices[1][0].stop
                            x_start, x_stop = object_slices[1][1].start, object_slices[1][1].stop
                            self.gt[z_id, y_start:y_stop, x_start:x_stop][reshape_labeled_array[0, y_start:y_stop, x_start:x_stop] == 2] = self.max_id + 1            
        else:
            print("Error: Exactly two annotation points with the same segment id are required to perform a split. ")
            return   

        self.max_id += 1
        self.gt_layer.invalidate()
        self.annotation_points = []
        with self.viewer.config_state.txn() as st:
            st.status_messages['split info'] = f"Splitting done!"
        print("Splitting done!")