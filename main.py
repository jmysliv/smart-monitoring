import cv2
from flask import Flask, render_template, Response, request, jsonify, after_this_request
import os
from camera import Camera
from object_detector import Detector
from frame_provider import FrameProvider
from recorder import Recorder
import json
from time import sleep
import threading
from flask import jsonify
from motor import Motor

app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')

motor = None

def load_config():
    with open('config.json') as json_file:
        data = json.load(json_file)
        Detector.set_threshold(float(data['threshold']))
        Recorder.set_observed_objects(set(data['observed_objects']))
        Recorder.set_record_length(int(data['record_length']))
        Recorder.set_button(int(data['button_pin']))
    Recorder()
    Camera()
    Detector()


def generate_frames(frame_provider: FrameProvider):
    while True:
        frame = frame_provider.get_frame()
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/configuration')
def index():
    return render_template('configuration/index.html')

@app.route('/')
@app.route('/live')
def live():
    with open('config.json') as json_file:
        data = json.load(json_file)
    return render_template('live/index.html', width=data["width"], height=data["height"])


@app.route('/detection')
def detection():
    with open('config.json') as json_file:
        data = json.load(json_file)
    return render_template('detection/index.html', width=data["width"], height=data["height"])


@app.route('/recordings')
def recordings():
    recordings = []
    for file in os.listdir("./static/recordings"):
        if file.endswith(".mp4"):
            recordings.append(file)
    return render_template('recordings/index.html', recordings=recordings)


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(Camera()), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/object_detection')
def object_detection():
    return Response(generate_frames(Detector()), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/move_left', methods=['POST'])
def move_left():
    motor.move_left()
    return "OK"

@app.route('/move_right', methods=['POST'])
def move_right():
    motor.move_right()
    return "OK"

@app.route('/configure', methods=['GET', 'POST'])
def configure():
    if request.method == 'POST':
        data = request.get_json()
        with open("config.json", "r+") as jsonFile:
            config = json.load(jsonFile)
            for key in data:
                config[key] = data[key]
            jsonFile.seek(0)
            json.dump(data, jsonFile)
            jsonFile.truncate()
            load_config()
            return "OK"
    else:
        with open('config.json') as json_file:
            data = json.load(json_file)
        return jsonify(data)


try:
    if __name__ == "__main__":
        motor = Motor(17, 1)
        # run server
        load_config()
        app.run(host='0.0.0.0', port=9002, threaded=True)
except KeyboardInterrupt:
    motor.cleanup()