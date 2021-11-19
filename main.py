import this

from picamera import PiCamera
from time import sleep
from sense_hat import SenseHat

import modules
from utils import *
from modules import *

recording_duration = 10
max_temp = 80


def main():
    camera = PiCamera()
    sense = SenseHat()

    # modules.init_sense(sense)

    overheating = False
    recording = True
    video_count = 1
    global_time = 0
    t = 0

    camera.start_recording(f'{recordings_home}/recording-{video_count}.h264')

    while True:

        sleep(1)

        # Checks if raspberry pi is overheating
        if overheating:
            if get_cpu_temperature() >= max_temp:
                if not overheating:
                    sense.clear()
                    camera.stop_recording()
                    overheating = True
                continue
            else:
                space_manager()

                video_count += 1
                camera.start_recording(f'/home/pi/Desktop/Recordings/recording-{video_count}.h264')
                t = 0
                overheating = False

        # Handle button press event
        joystick_events = sense.stick.get_events()
        print(joystick_events)
        if len(joystick_events) > 0:

            if joystick_events[0].action == "pressed":
                if recording:
                    recording = False
                    camera.stop_recording()
                    space_manager()
                else:
                    recording = True
                    video_count += 1
                    camera.start_recording(f'/home/pi/Desktop/Recordings/recording-{video_count}.h264')
                    t = 0

        # LED Grid recording blink
        recording_icon(sense, recording)
        show_storage_usage(sense)

        # Check if camera is supposed to be recording
        if not recording:
            continue

        # Update display text (showing time, speed and temperature)
        camera.annotate_text = display_details(global_time, 13, convert_temp(sense.get_temperature()))

        # Check if recording duration met
        if t == recording_duration:
            camera.stop_recording()
            # TODO: decide wether to have this be sync or async
            space_manager()

            video_count += 1
            camera.start_recording(f'{recordings_home}/recording-{video_count}.h264')
            t = 0

        global_time += 1
        t += 1

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
