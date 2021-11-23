import os

from sense_hat import SenseHat
from math import *
import shutil

velocity = 0
recordings_home = "/home/pi/Desktop/Recordings"
showing_overheat = False


def display_details(time, velocity, temperature):
    return f'Time: {time} seconds, Velocity: {velocity} mph, Temperature {temperature}'


def convert_temp(celsius):
    return round(celsius * 1.8 + 32)


def get_cpu_temperature():
    reader = open("/sys/class/thermal/thermal_zone0/temp")
    return float(reader.read()) / 1000


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


def space_manager():
    total, used, free = shutil.disk_usage("/")
    perc_used = used / total

    # TODO: display something when this condition is met
    if perc_used >= 0.90:
        files = os.listdir(recordings_home)
        if len(files) == 0:
            return

        files.sort(key=file_sort)

        f = files[0]
        os.remove(f'{recordings_home}/{f}')

        space_manager()


def file_sort(f: str):
    return int(f.split(".")[0].split("-")[1])


def get_count():
    file = open("count", "r")
    count = int(file.read())
    file.close()
    return count


def add_count(curr_count):
    curr_count += 1
    file = open("count", "w")
    file.write(f'{curr_count}')
    file.close()
    return curr_count


def show_temp_warning(sense):
    global showing_overheat

    if not showing_overheat:
        sense.clear()
        showing_overheat = True
    else:
        R = (255, 0, 0)
        O = (0, 0, 0)

        warning = [
            O, O, O, R, R, O, O, O,
            O, O, R, O, O, R, O, O,
            O, O, R, O, O, R, O, O,
            O, R, O, R, R, O, R, O,
            O, R, O, R, R, O, R, O,
            R, O, O, R, R, O, O, R,
            R, O, O, O, O, O, O, R,
            R, R, R, R, R, R, R, R,
        ]
        sense.set_pixels(warning)
        showing_overheat = False


def show_check(sense):
    O = (0, 0, 0)
    G = (0, 255, 0)

    check_mark = [
        O, O, O, O, O, O, O, O,
        O, G, O, O, O, O, O, O,
        O, O, G, O, O, O, O, O,
        O, O, G, O, O, O, O, O,
        O, O, O, G, O, O, G, O,
        O, O, O, G, O, G, O, O,
        O, O, O, O, G, O, O, O,
        O, O, O, O, O, O, O, O,
    ]
    sense.set_pixels(check_mark)


def drive_connected():
    media_files = os.listdir("/media/pi")

    return len(media_files) > 0


def get_drive_name():
    media_files = os.listdir("/media/pi")
    return media_files[0]


def transfer_files(transfer_all: bool):
    if not drive_connected():
        return

    drive_path = f'/media/pi/{get_drive_name()}/Transferred-Recordings'
    if not os.path.isdir(drive_path):
        os.mkdir(drive_path, 0o666)

    files = os.listdir(recordings_home)

    if not transfer_all:
        files.sort(key=file_sort, reverse=True)
        new_files = pop_front(files, 5)
    else:
        new_files = files

    for file in new_files:
        shutil.copyfile(f'{recordings_home}/{file}', f'{drive_path}/{file}')


def pop_front(array, pops):
    if len(array) < pops:
        pops = len(array)

    new_array = [None] * pops
    i = 0
    while i < pops:
        new_array[0] = array[i]

    return new_array
