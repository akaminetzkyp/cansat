import time
import datetime


class Logger:
    def __init__(self, bmp280, dht11, mpu9250):
        self.bmp280 = bmp280
        self.dht11 = dht11
        self.mpu9250 = mpu9250

        self.run = True

    def log(self):
        last_dht11_sample_time = 0
        row_counter = 0
        rows_text = ''

        formatted_datetime = datetime.datetime.utcnow().strftime(
            '%Y%m%d-%H%M%S')
        file_name = 'log_{}.csv'.format(formatted_datetime)
        with open(file_name, 'w') as file:
            header = ('Datetime,Temperature (BMP280),Pressure (BMP280),'
                      'Altitude (BMP280),Temperature (DHT11),Humidity (DHT11),'
                      'Acceleration X (MPU9250),Acceleration Y (MPU9250),'
                      'Acceleration Z (MPU9250),Gyroscope X (MPU9250),'
                      'Gyroscope Y (MPU9250),Gyroscope Z (MPU9250),'
                      'Magnetometer X (MPU9250),Magnetometer Y (MPU9250),'
                      'Magnetometer Z (MPU9250)\n')
            file.write(header)

        while self.run:
            row = [datetime.datetime.utcnow().isoformat()]

            row.extend(self.bmp280.read_last_data())

            if time.time() - last_dht11_sample_time > 2:
                dht11_data = self.dht11.read()
                row.extend([dht11_data.temperature, dht11_data.humidity])
            else:
                row.extend(['', ''])

            accel = self.mpu9250.readAccel()
            gyro = self.mpu9250.readGyro()
            mag = self.mpu9250.readMagnet()

            row.extend([accel['x'], accel['y'], accel['z'],
                        gyro['x'], gyro['y'], gyro['z'],
                        mag['x'], mag['y'], mag['z']])

            rows_text += ','.join(str(x) for x in row) + '\n'
            row_counter += 1

            if row_counter >= 20:
                with open(file_name, 'w') as file:
                    file.write(rows_text)
                rows_text = ''
                row_counter = 0

            time.sleep(0.1)
