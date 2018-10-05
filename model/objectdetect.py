from .base import BaseModel

import os
import tarfile
import tensorflow as tf
import numpy as np
from lib.object_detection.utils import label_map_util
from lib.object_detection.utils import visualization_utils as vis_util

MODEL_NAME = './lib/object_detection/ssd_mobilenet_v1_coco_11_06_2017'
MODEL_FILE = MODEL_NAME + '.tar.gz'
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'
PATH_TO_LABELS = os.path.join('./lib/object_detection/data', 'mscoco_label_map.pbtxt')

NUM_CLASSES = 90


class DetectionModel(BaseModel):
    def __init__(self, remote_controller):
        super(DetectionModel, self).__init__(remote_controller)

        tar_file = tarfile.open(MODEL_FILE)
        for file in tar_file.getmembers():
            file_name = os.path.basename(file.name)
            if 'frozen_inference_graph.pb' in file_name:
                tar_file.extract(file, os.getcwd())
        self.detection_graph = tf.Graph()

        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        self.label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
        self.categories = label_map_util.convert_label_map_to_categories(self.label_map, max_num_classes=NUM_CLASSES,
                                                                    use_display_name=True)
        self.category_index = label_map_util.create_category_index(self.categories)
        self.sess = tf.InteractiveSession(graph=self.detection_graph)

    def main(self, remote_controller, stream_receiver, frame):
        print('obj in')


        image_np_expanded = np.expand_dims(frame, axis=0)

        image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

        (boxes, scores, classes, num_detections) = self.sess.run(
            [boxes, scores, classes, num_detections],
            feed_dict={image_tensor: image_np_expanded})

        # Visualization of the results of a detection.

        # vis_util.visualize_boxes_and_labels_on_image_array(
        #     frame,
        #     np.squeeze(boxes),
        #     np.squeeze(classes).astype(np.int32),
        #     np.squeeze(scores),
        #     self.category_index,
        #     use_normalized_coordinates=True,
        #     line_thickness=8)

        for i, b in enumerate(boxes[0]):

            #                 car                    bus                  truck
            if classes[0][i] ==1 or classes[0][i] == 3 or classes[0][i] == 6 or classes[0][i] == 8:

                if scores[0][i] >= 0.5:
                    mid_x = (boxes[0][i][1] + boxes[0][i][3]) / 2

                    mid_y = (boxes[0][i][0] + boxes[0][i][2]) / 2
                    apx_distance = round(((1 - (boxes[0][i][3] - boxes[0][i][1])) ** 4), 1)

                    if apx_distance <= 0.5:
                        vec = [1]
                        stop_cmd = remote_controller.Command(16)
                        remote_controller.push_command(stop_cmd(vec))
                        return

        vec = [0]
        ready_cmd = remote_controller.Command(16)
        remote_controller.push_command(ready_cmd(vec))

        return


