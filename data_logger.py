class Logger:
    def __init__(self, bmp280, dht11, mpu9250):
        self.bmp280 = bmp280
        self.dht11 = dht11
        self.mpu9250 = mpu9250

        self.run = True

    def log_time(self, seconds):
        pass
