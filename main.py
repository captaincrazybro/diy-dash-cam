import this

from picamera import PiCamera
from time import sleep
from sense_hat import SenseHat

import modules
import utils
from utils import *
from modules import *

recording_duration = 10
max_temp = 80


def main():
    global max_temp
    camera = PiCamera()
    sense = SenseHat()

    # modules.init_sense(sense)

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

                convert_file(f'{recordings_home}/recording-{video_count}.h264')
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

            camera.start_recording(f'/home/pi/Desktop/Recordings/recording-{video_count}.h264')
            t = 0
            overheating = False

        # Handle button press event
        handled_button = handle_button(sense)
        if handled_button == 1:
            if recording:
                recording = False
                camera.stop_recording()
                convert_file(f'{recordings_home}/recording-{video_count}.h264')

                video_count = add_count(video_count)
                space_manager()
            else:
                recording = True
                camera.start_recording(f'/home/pi/Desktop/Recordings/recording-{video_count}.h264')
                t = 0
        if handled_button > 1:
            if recording:
                recording_icon(sense, False)
                camera.stop_recording()
                convert_file(f'{recordings_home}/recording-{video_count}.h264')
                video_count = add_count(video_count)

                print(os.listdir(recordings_home))
                utils.transfer_files(transfer_all=True if handled_button is 3 else False)

                space_manager()
                camera.start_recording(f'/home/pi/Desktop/Recordings/recording-{video_count}.h264')
                t = 0
                sleep(1)
            else:
                print("THIS CALLED")
                utils.transfer_files(transfer_all= True if handled_button is 3 else False)

        # LED Grid recording blink
        recording_icon(sense, recording)
        show_storage_usage(sense)

        # Check if camera is supposed to be recording
        if not recording:
            continue

        # Check if recording duration met
        if t == recording_duration:
            camera.stop_recording()
            convert_file(f'{recordings_home}/recording-{video_count}.h264')

            space_manager()

            video_count = add_count(video_count)
            camera.start_recording(f'{recordings_home}/recording-{video_count}.h264')
            t = 0

        # Update display text (showing time, speed and temperature)
        camera.annotate_text = display_details(global_time, 13, convert_temp(sense.get_temperature()))

        t += 1


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
