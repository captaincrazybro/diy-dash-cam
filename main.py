import os.path
import this

import picamera
from time import sleep
from sense_hat import SenseHat
import yaml

from utils import *
from modules import *

recording_duration = 10
max_temp = 80

def main():
    global max_temp
    import_config()

    camera = picamera.PiCamera()
    sense = SenseHat()
    gpsp = GpsPoller()
    sense.clear()

    overheating = False
    recording = True
    shown_gps_found = False
    show_clear = False
    video_count = utils.get_count()
    global_time = 0
    t = 1

    gpsp.start()
    camera.annotate_background = picamera.Color('black')
    camera.annotate_text = display_details(convert_temp(sense.get_temperature()))
    camera.start_recording(f'{recordings_home}/recording-{video_count}.h264')

    while True:

        global_time += 1
        sleep(1)

        # Checks if raspberry pi is overheating
        if get_cpu_temperature() >= max_temp:
            if not overheating:
                sense.clear()
                video_count = utils.stop_recording(camera, video_count)

                overheating = True
            utils.show_temp_warning(sense)
            continue
        elif overheating:
            utils.show_check(sense)
            sleep(1)
            sense.clear()
            sleep(1)

            t = utils.start_recording(camera, video_count, t)
            overheating = False

        # Handle button press event
        handled_button = handle_button(sense)
        if handled_button == 1:
            if recording:
                recording = False 
                video_count = utils.stop_recording(camera, video_count)

            else:
                t = utils.start_recording(camera, video_count, t)
                recording = True

        # Handle file transfer
        if handled_button > 1 and drive_connected():
            show_transferring(sense)
            if recording:
                recording_icon(sense, False)
                video_count = utils.stop_recording(camera, video_count)

                utils.transfer_files(transfer_all=True if handled_button is 3 else False)

                t = utils.start_recording(camera, video_count, t)
            else:
                utils.transfer_files(transfer_all=True if handled_button is 3 else False)

            sense.clear()
            sleep(1)
        # Handle button hold event
        if handled_button == -1 and drive_connected():
            if recording:
                video_count = utils.stop_recording(camera, video_count)
                utils.switch_drives(sense)

                t = utils.start_recording(camera, video_count, t)
            else:
                utils.switch_drives(sense)

        # Update LED grid
        if show_clear:
            sense.clear()

        if not shown_gps_found and gpsd_is_set():
            shown_gps_found = True
            show_gps_found(sense)
            show_clear = True
        else:
            recording_icon(sense, recording)
            show_storage_usage(sense)

        # Check if camera is supposed to be recording
        if not recording:
            continue

        # Check if recording duration met or switching storage
        if t == recording_duration:
            # TODO: make these into a function: start_recording() and stop_recording()
            video_count = utils.stop_recording(camera, video_count)
            t = utils.start_recording(camera, video_count, t)

        # Update display text (showing time, speed and temperature)
        camera.annotate_text = display_details(convert_temp(sense.get_temperature()))

        t += 1

def import_config():
    global max_temp, recording_duration
    if not os.path.isfile("config.yml"):
        new_file = open("config.yml", "w+")
        new_file.write("recording_duration: 900 #s\n" +
                       "max_temperature: 80 #C\n" +
                       "max_file_usage: 0.90 #* 100 %\n" +
                       "recordings_directory: \"/home/pi/Desktop/Recordings\"\n")
        new_file.close()

    config_file = open("config.yml", "r")
    config = yaml.safe_load(config_file)
    config_file.close()

    max_temp = config["max_temperature"]
    recording_duration = config["recording_duration"]
    utils.recordings_home = config["recordings_directory"]
    utils.max_file_usage = config["max_file_usage"]


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
