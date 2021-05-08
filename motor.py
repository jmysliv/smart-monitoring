import RPi.GPIO as GPIO
from time import sleep

class Motor():
    def __init__(self, servo_pin: int, moving_angle: int):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(servo_pin, GPIO.OUT)
        self.current_angle = 7
        self.moving_angle = moving_angle
        self.servo = GPIO.PWM(servo_pin, 50)
        self.servo.start(7)
        sleep(0.2)
        self.servo.ChangeDutyCycle(0)

    def move_left(self):
        if self.current_angle + self.moving_angle <= 12:
            self.servo.ChangeDutyCycle(self.current_angle + self.moving_angle)
            sleep(0.2)
            self.servo.ChangeDutyCycle(0)
            self.current_angle += self.moving_angle


    def move_right(self):
        if self.current_angle - self.moving_angle >= 2:
            self.servo.ChangeDutyCycle(self.current_angle - self.moving_angle)
            sleep(0.2)
            self.servo.ChangeDutyCycle(0)
            self.current_angle -= self.moving_angle

    def cleanup(self):
        self.servo.stop()
        GPIO.cleanup()
