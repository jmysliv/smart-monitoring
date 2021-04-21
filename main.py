import cv2
from flask import Flask, render_template, Response, request, jsonify, after_this_request
import os
from camera import Camera
from frame_provider import FrameProvider
from object_detector import Detector
import json

app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')


def generate_frames(frame_provider: FrameProvider):
    while True:
        frame = frame_provider.get_frame()
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('live/index.html')


@app.route('/live')
def live():
    return render_template('live/index.html')


@app.route('/detection')
def detection():
    return render_template('detection/index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(Camera()), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/object_detection')
def object_detection():
    return Response(generate_frames(Detector()), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    # run server
    app.run(host='0.0.0.0', port=9002, threaded=True)