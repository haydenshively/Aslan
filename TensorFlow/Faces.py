import numpy as np
import cv2
import tensorflow as tf
from queue import Queue, Empty

from TensorFlow.ByGoogle import label_map_util

enabled = False
queue_image = Queue()
queue_result = Queue()

# MODEL INITIALIZATION
path_to_ckpt = 'TensorFlow/Models/fullybaked/' + 'frozen_inference_graph.pb'
path_to_labels = 'TensorFlow/Data/Generated/' + 'FDDB_label_map.pbtxt'

num_classes = 1

detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(path_to_ckpt, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

label_map = label_map_util.load_labelmap(path_to_labels)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=num_classes, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

def run():
    enabled = True

    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

            detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
            detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
            detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name('num_detections:0')

            while enabled:
                # get image data
                image = queue_image.get(True)
                while True:
                    try:
                        image = queue_image.get_nowait()
                    except Empty:
                        break

                if image is 'break': break

                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image_expanded = np.expand_dims(image, axis = 0)

                # send image data through model
                (boxes, scores, classes, num) = sess.run([detection_boxes, detection_scores, detection_classes, num_detections], feed_dict={image_tensor: image_expanded})

                # filter results
                boxes_scoreChecked = boxes[scores > .3].tolist()
                boxes_shapeChecked = []
                for good_box in boxes_scoreChecked:
                    h = good_box[2] - good_box[0]
                    # w = good_box[3] - good_box[1]
                    if h > 0.1:
                        boxes_shapeChecked.append(good_box)

                # average results
                boxes = np.asarray(boxes_shapeChecked)
                if len(boxes.shape) is 2:
                    height, width = image.shape[:2]
                    mean = boxes.mean(axis = 0)
                    mean[0::2] *= height
                    mean[1::2] *= width
                    mean = mean.astype('uint16')

                    queue_result.put(mean)


def stop():
    enabled = False
