from picamera import PiCamera
from time import sleep
from sense_hat import SenseHat

from utils import *
from modules import *

recording_duration = 10
max_temp = 80

def main():
    camera = PiCamera()
    sense = SenseHat()

    overheating = False
    recording = True
    video_count = 1
    global_time = 0
    t = 0

    camera.start_preview()
    camera.start_recording(f'{recordings_home}/recording-{video_count}.h264')

    while True:

        # Checks if raspberry pi is overheating
        if overheating:
            if sense.get_cpu_temperature() >= max_temp:
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
        if len(joystick_events) > 0:
            recording = not recording

            if not recording:
                camera.stop_recording()
                space_manager()
                continue
            else:
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
        camera.annotate_text = display_details(global_time, round(get_velocity(), 0), convert_temp(sense.get_temperature()))

        # Check if recording duration met
        if t == recording_duration:
            camera.stop_recording()
            # TODO: decide wether to have this be sync or async
            space_manager()

            video_count += 1
            camera.start_recording(f'{recordings_home}/recording-{video_count}.h264')
            t = 0
            space_manager()

        sleep(1)
        global_time += 1
        t += 1

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
