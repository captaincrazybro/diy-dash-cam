import os

from sense_hat import SenseHat
from math import *
import shutil

velocity = 0

recordings_home = "/home/pi/Desktop/Recordings"


def display_details(time, velocity, temperature):
    return f'Time: {time} seconds, Velocity: {velocity} mph, Temperature {temperature}'


def convert_temp(celsius):
    return round(celsius * 1.8 + 32)


def get_cpu_temperature():
    reader = open("/sys/class/thermal/thermal_zone0/temp")
    return int(reader.read())


def get_acceleration():
    sense = SenseHat()

    raw = sense.get_accelerometer_raw()
    acc = mag(raw['x'], raw['y'], raw['z']) * 21.94
    print(raw['x'])
    print(acc)
    print(acc / 21.94)
    return acc


def mag(x, y, z):
    return sqrt(x ** 2 + y ** 2 + z ** 2)


def get_velocity():
    global velocity
    a = get_acceleration()
    dt = 1
    velocity += a * dt

    return velocity


async def space_manager():
    check_space()


def check_space():
    total, used, free = shutil.disk_usage("/")
    perc_used = used / total

    if perc_used >= 0.90:
        files = os.listdir(recordings_home)
        files.sort(key=file_sort)

        f = files[0]
        os.remove(f)

        check_space()


def file_sort(f: str):
    return int(f.split(".")[0].split("-")[1])
