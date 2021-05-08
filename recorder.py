from object_detector import Detector
from camera import Camera
import time
from time import sleep
import ffmpeg
import cv2
import threading
from gpiozero import Button

class Recorder(object):
    thread = None
    observed_objects = None
    record_length = None
    isRecording = False
    buttonPin = None
    button = None

    @classmethod
    def set_observed_objects(cls, observed_objects: set):
        Recorder.observed_objects = observed_objects

    @classmethod
    def set_record_length(cls, record_length: int):
        Recorder.record_length = record_length

    @classmethod
    def set_button(cls, buttonPin: int):
        if Recorder.buttonPin != buttonPin:
            Recorder.buttonPin = buttonPin
            Recorder.button = Button(buttonPin)

    def __init__(self):
        Detector.register_observer(self)
        if Recorder.thread is None:
            Recorder.thread = threading.Thread(target=self.listen_button_event).start()

    def listen_button_event(self):
         while True:
            if Recorder.button.is_pressed:
                print("Button is pressed")
                self.can_record()
                sleep(Recorder.record_length)
            sleep(1)

    def can_record(self, detected_objects=None):
        if detected_objects != None:
            if not Recorder.isRecording:
                for detected in detected_objects:
                    if detected in Recorder.observed_objects:
                        threading.Thread(target=self.record).start()
                        break
        else:
            if not Recorder.isRecording:
                threading.Thread(target=self.record).start()

    def record(self):
        Recorder.isRecording = True
        print("Recording started")
        camera = Camera()
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        timestamp = time.strftime("%d\%m\%Y_%H:%M:%S")
        directory = 'static/recordings/'
        frames = []
        start = time.time()
        while int(time.time() - start) < Recorder.record_length:
            frames.append(camera.get_frame())
            time.sleep(0.03)
        fps = len(frames)/Recorder.record_length
        out = cv2.VideoWriter(directory + timestamp + '.avi', fourcc, fps, (640,480))
        for frame in frames:
            out.write(frame)
        out.release()
        stream = ffmpeg.input(directory + timestamp + '.avi')
        stream = ffmpeg.hflip(stream)
        stream = ffmpeg.output(stream, directory + timestamp + '.mp4')
        ffmpeg.run(stream)
        Recorder.isRecording = False
