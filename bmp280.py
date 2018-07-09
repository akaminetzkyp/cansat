#!/usr/bin/python
# --------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#           bme280.py
#  Read data from a digital pressure sensor.
#
#  Official datasheet available from :
#  https://www.bosch-sensortec.com/bst/products/all_products/bme280
#
# Author : Matt Hawkins (Modified by Alejandro Kaminetzky)
# Date   : 25/07/2016
#
# http://www.raspberrypi-spy.co.uk/
#
# --------------------------------------

import smbus
import time
from ctypes import c_short
import math


class BMP280:

    def __init__(self, min_delay):
        self.DEVICE = 0x76  # Default device I2C address
        self.bus = smbus.SMBus(1)  # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1, Rev 1 Pi
        # uses bus 0

        self.min_delay = min_delay
        self.last_sample_time = 0
        self.last_temperature = 0
        self.last_pressure = 0
        self.last_altitude = 0

    @staticmethod
    def get_short(data, index):
        # Return two bytes from data as a signed 16-bit value
        return c_short((data[index+1] << 8) + data[index]).value

    @staticmethod
    def get_u_short(data, index):
        # Return two bytes from data as an unsigned 16-bit value
        return (data[index+1] << 8) + data[index]

    @staticmethod
    def get_char(self, data, index):
        # Return one byte from data as a signed char
        result = data[index]
        if result > 127:
            result -= 256
        return result

    @staticmethod
    def get_u_char(data, index):
        # Return one byte from data as an unsigned char
        result = data[index] & 0xFF
        return result

    def read_id(self, addr=None):
        addr = addr if addr is not None else self.DEVICE

        # Chip ID Register Address
        reg_id = 0xD0
        (chip_id, chip_version) = self.bus.read_i2c_block_data(addr, reg_id, 2)
        return chip_id, chip_version

    def read_data(self, addr=None):
        addr = addr if addr is not None else self.DEVICE

        # Register Addresses
        reg_data = 0xF7
        reg_control = 0xF4

        reg_control_hum = 0xF2

        # Oversample setting - page 27
        oversample_temp = 2
        oversample_pres = 2
        mode = 1

        # Oversample setting for humidity register - page 26
        oversample_hum = 2
        self.bus.write_byte_data(addr, reg_control_hum, oversample_hum)

        control = oversample_temp << 5 | oversample_pres << 2 | mode
        self.bus.write_byte_data(addr, reg_control, control)

        # Read blocks of calibration data from EEPROM
        # See Page 22 data sheet
        cal1 = self.bus.read_i2c_block_data(addr, 0x88, 24)

        # Convert byte data to word values
        dig_t1 = BMP280.get_u_short(cal1, 0)
        dig_t2 = BMP280.get_short(cal1, 2)
        dig_t3 = BMP280.get_short(cal1, 4)

        dig_p1 = BMP280.get_u_short(cal1, 6)
        dig_p2 = BMP280.get_short(cal1, 8)
        dig_p3 = BMP280.get_short(cal1, 10)
        dig_p4 = BMP280.get_short(cal1, 12)
        dig_p5 = BMP280.get_short(cal1, 14)
        dig_p6 = BMP280.get_short(cal1, 16)
        dig_p7 = BMP280.get_short(cal1, 18)
        dig_p8 = BMP280.get_short(cal1, 20)
        dig_p9 = BMP280.get_short(cal1, 22)

        # Wait in ms (Datasheet Appendix B:
        # Measurement time and current calculation)
        wait_time = 1.25 + (2.3 * oversample_temp) + ((2.3 * oversample_pres) +
                                                      0.575) + ((2.3
                                                                *
                                                                 oversample_hum)
                                                                + 0.575)
        time.sleep(wait_time/1000)  # Wait the required time

        # Read temperature/pressure/humidity
        data = self.bus.read_i2c_block_data(addr, reg_data, 8)
        pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)

        # Refine temperature
        var1 = (((temp_raw >> 3) - (dig_t1 << 1)) * dig_t2) >> 11
        var2 = (((((temp_raw >> 4) - dig_t1) * ((temp_raw >> 4) - dig_t1)) >> 12)
                * dig_t3) >> 14
        t_fine = var1 + var2
        temperature = float(((t_fine * 5) + 128) >> 8)

        # Refine pressure and adjust for temperature
        var1 = t_fine / 2.0 - 64000.0
        var2 = var1 * var1 * dig_p6 / 32768.0
        var2 = var2 + var1 * dig_p5 * 2.0
        var2 = var2 / 4.0 + dig_p4 * 65536.0
        var1 = (dig_p3 * var1 * var1 / 524288.0 + dig_p2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * dig_p1
        if var1 == 0:
            pressure = 0
        else:
            pressure = 1048576.0 - pres_raw
            pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
            var1 = dig_p9 * pressure * pressure / 2147483648.0
            var2 = pressure * dig_p8 / 32768.0
            pressure = pressure + (var1 + var2 + dig_p7) / 16.0

        temperature = temperature / 100
        pressure = pressure / 1000

        altitude = -44330.7694402059 * (10 ** ((math.log10(pressure / 101.325))
                                               / 5.2558797) - 1)

        self.last_sample_time = time.time()
        self.last_temperature = temperature
        self.last_pressure = pressure
        self.last_altitude = altitude

        return temperature, pressure, altitude

    def read_last_data(self, addr=None):
        addr = addr if addr is not None else self.DEVICE
        if time.time() - self.last_sample_time > self.min_delay:
            self.last_temperature, self.last_pressure, self.last_altitude = (
                self.read_data())
            self.last_sample_time = time.time()
        return self.last_temperature, self.last_pressure, self.last_altitude

    def main(self):
        temperature, pressure, altitude = self.read_data()

        print("Temperature: ", temperature, "C")
        print("Pressure: ", pressure, "kPa")
        print("Altitude: ", altitude, "m")


if __name__ == "__main__":
    bmp280_0 = BMP280()
    bmp280_0.main()
