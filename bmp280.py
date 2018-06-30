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
# Author : Matt Hawkins
# Date   : 25/07/2016
#
# http://www.raspberrypi-spy.co.uk/
#
# --------------------------------------
import smbus
import time
from ctypes import c_short

DEVICE = 0x76  # Default device I2C address


bus = smbus.SMBus(1)  # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1, Rev 1 Pi uses bus 0


def get_short(data, index):
    # return two bytes from data as a signed 16-bit value
    return c_short((data[index+1] << 8) + data[index]).value


def get_u_short(data, index):
    # return two bytes from data as an unsigned 16-bit value
    return (data[index+1] << 8) + data[index]


def get_char(data, index):
    # return one byte from data as a signed char
    result = data[index]
    if result > 127:
        result -= 256
    return result


def get_u_char(data, index):
    # return one byte from data as an unsigned char
    result = data[index] & 0xFF
    return result


def read_id(addr=DEVICE):
    # Chip ID Register Address
    reg_id = 0xD0
    (chip_id, chip_version) = bus.read_i2c_block_data(addr, reg_id, 2)
    return chip_id, chip_version


def read_data(addr=DEVICE):
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
    bus.write_byte_data(addr, reg_control_hum, oversample_hum)

    control = oversample_temp << 5 | oversample_pres << 2 | mode
    bus.write_byte_data(addr, reg_control, control)
  
    # Read blocks of calibration data from EEPROM
    # See Page 22 data sheet
    cal1 = bus.read_i2c_block_data(addr, 0x88, 24)
  
    # Convert byte data to word values
    dig_t1 = get_u_short(cal1, 0)
    dig_t2 = get_short(cal1, 2)
    dig_t3 = get_short(cal1, 4)
  
    dig_p1 = get_u_short(cal1, 6)
    dig_p2 = get_short(cal1, 8)
    dig_p3 = get_short(cal1, 10)
    dig_p4 = get_short(cal1, 12)
    dig_p5 = get_short(cal1, 14)
    dig_p6 = get_short(cal1, 16)
    dig_p7 = get_short(cal1, 18)
    dig_p8 = get_short(cal1, 20)
    dig_p9 = get_short(cal1, 22)

    # Wait in ms (Datasheet Appendix B:
    # Measurement time and current calculation)
    wait_time = 1.25 + (2.3 * oversample_temp) + ((2.3 * oversample_pres) +
                                                  0.575) + ((2.3
                                                            * oversample_hum)
                                                            + 0.575)
    time.sleep(wait_time/1000)  # Wait the required time  
  
    # Read temperature/pressure/humidity
    data = bus.read_i2c_block_data(addr, reg_data, 8)
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
  
    return temperature/100.0, pressure/100.0


def main():
    (chip_id, chip_version) = read_id()
    print("Chip ID:", chip_id)
    print("Version:", chip_version)

    temperature, pressure = read_data()

    print("Temperature: ", temperature, "ºC")
    print("Pressure: ", pressure, "hPa")


if __name__ == "__main__":
    main()
