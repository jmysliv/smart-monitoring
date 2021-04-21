import cv2
import threading
import time
from frame_provider import FrameProvider
from camera import Camera


class Detector(FrameProvider):
    thread = None
    frame = None
    threshold = 0.7
    observer = None

    def __init__(self):
        if Detector.thread is None:
            Detector.thread = threading.Thread(
                target=self.thread_job, args=(Camera(),))
            Detector.thread.start()

        while self.get_frame() is None:
            time.sleep(0)

    def get_frame(self):
        return Detector.frame

    @classmethod
    def set_threshold(cls, threshold: int):
        Detector.threshold = threshold

    @classmethod
    def register_observer(cls, observer):
        Detector.observer = observer

    @classmethod
    def notify_observer(cls, detected_objects: set):
        if Detector.observer != None:
            Detector.observer.can_record(detected_objects)

    @classmethod
    def thread_job(cls, camera: Camera):
        print('Starting object detection.')
        classes = []
        with open('data/coco.names', 'rt') as f:
            classes = f.read().rstrip('\n').split('\n')
        config_file = 'data/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
        weights_file = 'data/frozen_inference_graph.pb'
        net = cv2.dnn_DetectionModel(weights_file, config_file)
        net.setInputSize(320, 320)
        net.setInputScale(1.0 / 127.5)
        net.setInputMean((127.5, 127.5, 127.5))
        net.setInputSwapRB(True)
        while True:
            frame = camera.get_frame()
            class_ids, confidences, bbox = net.detect(
                frame, confThreshold=Detector.threshold)
            if len(class_ids) != 0:
                detected_objects = set()
                for class_id, confidence, box in zip(class_ids.flatten(), confidences.flatten(), bbox):
                    detected_objects.add(classes[class_id - 1])
                    cv2.rectangle(frame, box, color=(0, 255, 0), thickness=2)
                    cv2.putText(frame, classes[class_id-1].upper(), (box[0]+10,
                                box[1]+30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, str(round(
                        confidence*100)), (box[2]-50, box[1] + 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                Detector.notify_observer(detected_objects)

            Detector.frame = frame
            time.sleep(0.03)
