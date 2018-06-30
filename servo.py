import RPi.GPIO as GPIO


# La posición del servo es un número entre 0 y 1
class Servo:
    def __init__(self, pos):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.OUT)
        self.pwm = GPIO.PWM(18, 50)
        pos = min(max(pos, 0), 1)
        self.pwm.start(10 * pos + 3)
        
    def change_pos(self, pos):
        pos = min(max(pos, 0), 1)
        self.pwm.ChangeDutyCycle(10 * pos + 3)
        
    def stop(self):
        self.pwm.stop()
