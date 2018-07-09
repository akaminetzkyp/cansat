import threading
import time
import datetime
import bmp280
import dht11
import mpu9250
import servo
import parachute_deployer
import data_logger
import camera


def exit_script(deployer_0, logger_0, camera_0):
    formatted_time = datetime.datetime.utcnow().isoformat()
    print('[{}][exit_script] Exiting'.format(formatted_time))
    deployer_0.run = False
    logger_0.run = False
    camera_0.stop_recording()


def finisher_input(deployer_0, logger_0, camera_0):
    while True:
        input_text = input()
        if input_text == 'exit':
            exit_script(deployer_0, logger_0, camera_0)


def finisher_time(deployer_0, logger_0, camera_0, max_time):
    time.sleep(max_time)
    exit_script(deployer_0, logger_0, camera_0)


def main(max_time, altitude_dif, delay_sample):
    formatted_time = datetime.datetime.utcnow().isoformat()
    print('[{}][main] Starting main'.format(formatted_time))

    bmp280_0 = bmp280.BMP280(delay_sample - 0.01)
    dht11_0 = dht11.DHT11(pin=4)
    mpu9250_0 = mpu9250.MPU9250()
    servo_0 = servo.Servo(0)

    deployer_0 = parachute_deployer.Deployer(bmp280_0, servo_0, altitude_dif,
                                             delay_sample)
    logger_0 = data_logger.Logger(bmp280_0, dht11_0, mpu9250_0)
    camera_0 = camera.Camera()

    deployer_thread = threading.Thread(target=deployer_0.main)
    logging_thread = threading.Thread(target=logger_0.log)

    deployer_thread.start()
    logging_thread.start()

    camera_0.start_recording()

    finisher_input_thread = threading.Thread(target=finisher_input,
                                             args=(deployer_0, logger_0,
                                                   camera_0), daemon=True)
    finisher_time_thread = threading.Thread(target=finisher_time,
                                            args=(deployer_0, logger_0,
                                                  camera_0, max_time),
                                            daemon=True)
    finisher_input_thread.start()
    finisher_time_thread.start()


if __name__ == '__main__':
    max_time_0 = 600
    altitude_dif_0 = 2
    delay_sample_0 = 0.05
    main(max_time_0, altitude_dif_0, delay_sample_0)
