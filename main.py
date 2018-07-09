import threading
import time
import sys
import datetime
import bmp280
import dht11
import mpu9250
import servo
import parachute_deployer
import data_logger
import camera


def main(altitude_dif, delay_sample):
    formatted_time = datetime.datetime.utcnow().isoformat()
    print('[{}][main] Starting main'.format(formatted_time))

    bmp280_0 = bmp280.BMP280(delay_sample - 0.01)
    dht11_0 = dht11.DHT11(pin=4)
    mpu9250_0 = mpu9250.MPU9250()
    servo_0 = servo.Servo(0)

    deployer_0 = parachute_deployer.Deployer(bmp280_0, servo_0, altitude_dif,
                                             delay_sample)
    camera_0 = camera.Camera()
    logger_0 = data_logger.Logger(bmp280_0, dht11_0, mpu9250_0)

    deployer_thread = threading.Thread(target=deployer_0.main)
    camera_thread = threading.Thread(target=camera_0.record_time, args=(600,))
    logging_thread = threading.Thread(target=logger_0.log_time, args=(600,))

    deployer_thread.start()
    camera_thread.start()
    logging_thread.start()

    while True:
        input_text = input()
        if input_text == 'exit':
            deployer_0.run = False
            camera_0.stop_recording()
            logger_0.run = False
            formatted_time = datetime.datetime.utcnow().isoformat()
            print('[{}][main] Exiting in 2 seconds'.format(formatted_time))
            time.sleep(2)
            sys.exit()


if __name__ == '__main__':
    altitude_dif_0 = 2
    delay_sample_0 = 0.05
    main(altitude_dif_0, delay_sample_0)
