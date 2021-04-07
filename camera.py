import threading
import cv2
import time
from frame_provider import FrameProvider

class Camera(FrameProvider):
    frame = None
    thread = None

    def __init__(self):
        if Camera.thread is None:
            Camera.thread = threading.Thread(target=self.thread_job)
            Camera.thread.start()

        while self.get_frame() is None:
                time.sleep(0)
        
    def get_frame(self):
        return Camera.frame

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')
        while True:
            success, frame = camera.read()
            if success:
                yield frame


    @classmethod
    def thread_job(cls):
        print('Starting camera thread.')
        frames_iterator = cls.frames()
        for frame in frames_iterator:
            Camera.frame = frame