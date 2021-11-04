from sense_hat import SenseHat
from math import *

velocity = 0


def display_details(time, velocity, temperature):
    return f'Time: {time} seconds, Velocity: {velocity} mph, Temperature {temperature}'


def convert_temp(celsius):
    return celsius * 1.8 + 32


def get_cpu_temperature():
    reader = open("/sys/class/thermal/thermal_zone0/temp")
    return int(reader.read())


def get_acceleration():
    sense = SenseHat()

    raw = sense.get_accelerometer_raw()
    print(raw)
    return mag(raw.x, raw.y, raw.z) * 21.94


def mag(x, y, z):
    return sqrt(x**2 + y**2 + z**2)


def get_velocity():
    global velocity
    a = get_acceleration()
    dt = 1
    velocity += a * dt

    return velocity
