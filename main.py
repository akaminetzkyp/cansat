import RPi.GPIO as GPIO
import servo
import bmp280
import time
import datetime


def main():
    with open('/home/pi/Desktop/CanSat/log.txt', 'a') as file:
        try:
            altitude_dif = 2
            samples = 10
            delay_sample = 0.05

            altitude_max = -float('inf')

            servo_1 = servo.Servo(0)

            print('Beginning altitude check.')

            text = datetime.datetime.utcnow().isoformat() + ' - '
            text += 'Starting script.\n'
            file.write(text)

            while True:
                data_list = []
                for _ in range(samples):
                    temperature, pressure, altitude = bmp280.read_data()
                    data_list.append(altitude)
                    time.sleep(delay_sample)
                altitude_mean = sum(data_list) / samples
                altitude_max = max(altitude_max, altitude_mean)

                if altitude_mean < altitude_max - altitude_dif:
                    print('Deploying parachute. Resetting in 60 seconds.')
                    servo_1.change_pos(1)

                    text = datetime.datetime.utcnow().isoformat() + ' - '
                    text += 'Deploying parachute - '
                    text += 'Altitude: ' + str(altitude_mean) + ' - '
                    text += 'Max Altitude: ' + str(altitude_max) + '\n'
                    file.write(text)

                    time.sleep(60)
                    servo_1.change_pos(0)
                    altitude_max = -float("inf")
                else:
                    text = datetime.datetime.utcnow().isoformat() + ' - '
                    text += 'Altitude: ' + str(altitude_mean) + ' - '
                    text += 'Max Altitude: ' + str(altitude_max) + '\n'
                    file.write(text)
        except KeyboardInterrupt:
            servo_1.stop()
            GPIO.cleanup()
            print('Terminating script.')

            text = datetime.datetime.utcnow().isoformat() + ' - '
            text += 'Terminating script.\n'
            file.write(text)

if __name__ == '__main__':
    main()
