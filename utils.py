import os

from sense_hat import SenseHat
from math import *
import shutil
from subprocess import call
from time import sleep
from gps import *
import threading

velocity = 0
recordings_home = "/home/pi/Desktop/Recordings"
showing_overheat = False
use_drive = False
max_file_usage = 0.90
gpsd = None  # setting the global variable


class GpsPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd  # bring it in scope
        gpsd = gps(mode=WATCH_ENABLE)  # starting the stream of info
        self.current_value = None
        self.running = True  # setting the thread running to true

    def run(self):
        global gpsd
        while self.running:
            gpsd.next()  # this will continue to loop and grab EACH set of gpsd info to clear the buffer


def display_details(temperature):
    if gpsd is None:
        return 'Obtaining GPS...'

    print(gpsd if gpsd is None else gpsd.fix.speed)
    return f'{gpsd.utc}   {parse_velocity(gpsd.fix.speed)} mph   {temperature} C'


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
    if use_drive:
        return

    total, used, free = shutil.disk_usage("/")
    perc_used = used / total

    # TODO: display something when this condition is met
    if perc_used >= max_file_usage:
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
        OR = (255, 165, 0)

        warning = [
            O, O, O, R, R, O, O, O,
            O, O, R, OR, OR, R, O, O,
            O, O, R, OR, OR, R, O, O,
            O, R, O, OR, OR, O, R, O,
            O, R, OR, O, O, OR, R, O,
            R, O, OR, O, O, OR, O, R,
            R, O, O, OR, OR, O, O, R,
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
        new_file = f'{drive_path}/{file}'
        if not os.path.isfile(new_file):
            shutil.copyfile(f'{recordings_home}/{file}', new_file)


def pop_front(array, pops):
    if len(array) < pops:
        pops = len(array)

    new_array = [None] * pops
    i = 0
    while i < pops:
        new_array[i] = array[i]
        i += 1

    return new_array


def convert_file(file):
    mp4_file = file.split(".")[0] + ".mp4"

    command = "ffmpeg -framerate 25 -i \"" + file + "\" -c copy \"" + mp4_file + "\""
    call([command], shell=True)

    os.remove(file)


def show_transferring(sense):
    sense.clear()

    O = (0, 0, 0)
    G = (0, 255, 0)

    display = [
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, G, O, O, O, O,
        G, G, G, G, G, O, G, G,
        G, G, G, G, G, O, G, G,
        O, O, O, G, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
    ]

    sense.set_pixels(display)


def get_recordings_dir():
    global use_drive
    if use_drive and not drive_connected():
        use_drive = False

    if use_drive:
        path = f'/media/pi/{get_drive_name()}/Recordings'
        if not os.path.isdir(path):
            os.mkdir(path, 0o666)

        return path
    else:
        return recordings_home


def show_storage_switch(sense):
    if use_drive:
        O = (0, 0, 0)
        G = (0, 255, 0)
        W = (255, 255, 255)

        drive_display = [
            O, O, W, W, W, W, O, O,
            O, O, W, O, O, W, O, O,
            O, O, W, W, W, W, O, O,
            O, G, G, G, G, G, G, O,
            O, G, G, W, G, G, G, O,
            O, G, G, W, W, G, G, O,
            O, G, G, G, W, G, G, O,
            O, G, G, G, G, G, G, O,
        ]

        sense.set_pixels(drive_display)

    else:
        B = (0, 0, 0)
        G = (0, 255, 0)
        O = (255, 165, 0)

        dashpi_display = [
            B, B, B, B, B, B, B, B,
            B, B, B, B, B, B, B, B,
            B, B, B, O, O, O, O, B,
            B, G, G, O, B, O, B, B,
            B, B, B, O, B, O, B, B,
            B, B, B, O, B, O, B, B,
            B, B, B, B, B, B, B, B,
            B, B, B, B, B, B, B, B,
        ]

        sense.set_pixels(dashpi_display)


def switch_drives(sense):
    global use_drive
    sense.clear()
    use_drive = not use_drive
    show_storage_switch(sense)

    sleep(1)
    sense.clear()

    sense.stick.get_events()


def stop_recording(camera, video_count):
    camera.stop_recording()
    convert_file(f'{get_recordings_dir()}/recording-{video_count}.h264')
    video_count = add_count(video_count)

    return video_count


def start_recording(camera, video_count, t):
    space_manager()

    camera.start_recording(f'{get_recordings_dir()}/recording-{video_count}.h264')
    t = 0

    return t


def parse_velocity(velocity):
    if f'{velocity}' == 'nan':
        return 0
    else:
        return round(velocity)


def show_gps_found(sense):
    O = (0, 0, 0)
    W = (255, 255, 255)

    gps_found = [
        O, O, O, O, O, O, O, O,
        O, O, W, W, W, W, O, O,
        O, W, O, O, O, O, W, O,
        O, O, O, W, W, O, O, O,
        O, O, W, O, O, W, O, O,
        O, O, O, W, W, O, O, O,
        O, O, O, W, W, O, O, O,
        O, O, O, O, O, O, O, O,
    ]

    sense.set_pixels(gps_found)