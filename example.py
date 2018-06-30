import servo
import bmp280
import dht11
import mpu9250
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
    mpu9250_1 = mpu9250.MPU9250()
    accel = mpu9250_1.readAccel()
    
    
    print('MPU9250')
    
    print("ax =", (accel['x']))
    print("ay =", (accel['y']))
    print("az =", (accel['z']))

    gyro = mpu9250_1.readGyro()
    print("gx =", (gyro['x']))
    print("gy =", (gyro['y']))
    print("gz =", (gyro['z']))

    mag = mpu9250_1.readMagnet()
    print("mx =", (mag['x']))
    print("my =", (mag['y']))
    print("mz =", (mag['z']))
    print()


if __name__ == '__main__':
    pass
    # servo_example()
    # bmp280_example()
    # dht11_example()
    # mpu9250_example()
    