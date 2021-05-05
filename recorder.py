from object_detector import Detector
from camera import Camera
import time
import ffmpeg
import cv2
import threading

class Recorder(object):
    def __init__(self,observed_objects: set, record_length: int):
        self.observed_objects = observed_objects
        self.record_length = record_length
        self.isRecording = False
        Detector.register_observer(self)

    def can_record(self, detected_objects):
        if not self.isRecording:
            for detected in detected_objects:
                if detected in self.observed_objects:
                    threading.Thread(target=self.record).start()
                    break

    def record(self):
        self.isRecording = True
        print("Recording started")
        camera = Camera()
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        timestamp = time.strftime("%d\%m\%Y_%H:%M:%S")
        directory = 'static/recordings/'
        out = cv2.VideoWriter(directory + timestamp + '.avi', fourcc, 30, (640,480))
        start = time.time()
        while int(time.time() - start) < self.record_length:   
            frame = camera.get_frame()
            time.sleep(0.03)
            out.write(frame)

        out.release()
        stream = ffmpeg.input(directory + timestamp + '.avi')
        stream = ffmpeg.hflip(stream)
        stream = ffmpeg.output(stream, directory + timestamp + '.mp4')
        ffmpeg.run(stream)
        self.isRecording = False
