import servo
import bmp280
import dht11
import RPi.GPIO as GPIO
import time


def servo_example():
    # Pin 18
    servo_1 = servo.Servo(0)
    time.sleep(1)
    servo_1.change_pos(0.5)
    time.sleep(1)
    servo_1.stop()
    GPIO.cleanup()


def bmp280_example():
    # Pin SDA1 and SCL1
    temperature, pressure, altitude = bmp280.read_data()
    print('BMP280')
    print("Temperature: ", temperature, "C")
    print("Pressure: ", pressure, "kPa")
    print("Altitude: ", altitude, "m\n")


def dht11_example():
    # Pin 4
    dht11_1 = dht11.DHT11(pin=4)
    result = dht11_1.read()
    print('DHT11')
    print("Temperature: ", result.temperature, "C")
    print("HUmidity: ", result.humidity, "%\n")


def mpu9250_example():
    pass


if __name__ == '__main__':
    servo_example()
    bmp280_example()
    dht11_example()
