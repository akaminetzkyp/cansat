import time
import datetime
import RPi.GPIO as GPIO


class Deployer:
    def __init__(self, bmp280, servo, altitude_dif, delay_sample):
        self.bmp280 = bmp280
        self.servo = servo
        self.altitude_dif = altitude_dif
        self.delay_sample = delay_sample

        self.run = True

    def main(self):
        samples = 10

        altitude_max = -float('inf')

        formatted_time = datetime.datetime.utcnow().isoformat()
        print('[{}][Deployer.main] Beginning altitude check'.format(
            formatted_time))

        while self.run:
            data_list = []
            for _ in range(samples):
                temperature, pressure, altitude = (
                    self.bmp280.read_last_data())
                data_list.append(altitude)
                time.sleep(self.delay_sample)
            altitude_mean = sum(data_list) / samples
            altitude_max = max(altitude_max, altitude_mean)

            if altitude_mean < altitude_max - self.altitude_dif:
                formatted_time = datetime.datetime.utcnow().isoformat()
                print('[{}][Deployer.main] Deploying parachute. Resetting in '
                      '60 seconds')
                self.servo.change_pos(1)

                for _ in range(60):
                    if self.run:
                        time.sleep(1)

                self.servo.change_pos(0)
                altitude_max = -float("inf")

        self.servo.stop()
        GPIO.cleanup()
        formatted_time = datetime.datetime.utcnow().isoformat()
        print('[{}][Deployer.main] Stopping'.format(formatted_time))
