import os.path
import this

from picamera import PiCamera
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

    camera = PiCamera()
    sense = SenseHat()
    sense.clear()

    overheating = False
    recording = True
    video_count = utils.get_count()
    global_time = 0
    t = 1

    camera.annotate_text = display_details(global_time, 13, convert_temp(sense.get_temperature()))
    camera.start_recording(f'{recordings_home}/recording-{video_count}.h264')

    while True:

        global_time += 1
        sleep(1)

        # Checks if raspberry pi is overheating
        if get_cpu_temperature() >= max_temp:
            if not overheating:
                sense.clear()
                camera.stop_recording()

                convert_file(f'{get_recordings_dir()}/recording-{video_count}.h264')
                video_count = add_count(video_count)

                overheating = True
            utils.show_temp_warning(sense)
            continue
        elif overheating:
            utils.show_check(sense)
            sleep(1)
            sense.clear()
            sleep(1)

            space_manager()

            camera.start_recording(f'{get_recordings_dir()}/recording-{video_count}.h264')
            t = 0
            overheating = False

        # Handle button press event
        handled_button = handle_button(sense)
        if handled_button == 1:
            if recording:
                recording = False
                camera.stop_recording()
                convert_file(f'{get_recordings_dir()}/recording-{video_count}.h264')

                video_count = add_count(video_count)
                space_manager()
            else:
                recording = True
                camera.start_recording(f'{get_recordings_dir()}/recording-{video_count}.h264')
                t = 0
        if handled_button > 1 and drive_connected():
            show_transferring(sense)
            if recording:
                recording_icon(sense, False)
                camera.stop_recording()
                convert_file(f'{get_recordings_dir()}/recording-{video_count}.h264')
                video_count = add_count(video_count)

                utils.transfer_files(transfer_all=True if handled_button is 3 else False)

                space_manager()
                camera.start_recording(f'{get_recordings_dir()}/recording-{video_count}.h264')
                t = 0
            else:
                utils.transfer_files(transfer_all=True if handled_button is 3 else False)

            sense.clear()
            sleep(1)
        if handled_button == -1 and drive_connected():
            if recording:
                camera.stop_recording()
                convert_file(f'{get_recordings_dir()}/recording-{video_count}.h264')

                utils.switch_drives(sense)

                space_manager()

                video_count = add_count(video_count)
                camera.start_recording(f'{get_recordings_dir()}/recording-{video_count}.h264')
                t = 0
            else:
                utils.switch_drives(sense)

        # LED Grid recording blink
        recording_icon(sense, recording)
        show_storage_usage(sense)

        # Check if camera is supposed to be recording
        if not recording:
            continue

        # Check if recording duration met or switching storage
        if t == recording_duration:
            # TODO: make these into a function: start_recording() and stop_recording()
            camera.stop_recording()
            convert_file(f'{get_recordings_dir()}/recording-{video_count}.h264')

            space_manager()

            video_count = add_count(video_count)
            camera.start_recording(f'{get_recordings_dir()}/recording-{video_count}.h264')
            t = 0

        # Update display text (showing time, speed and temperature)
        camera.annotate_text = display_details(global_time, 13, convert_temp(sense.get_temperature()))

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
