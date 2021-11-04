from picamera import PiCamera
from time import sleep
from sense_hat import SenseHat

from utils import *

recording_duration = 10
max_temp = 80

def main():
    camera = PiCamera()
    sense = SenseHat()

    overheating = False
    video_count = 1
    global_time = 0
    t = 0

    camera.start_preview()
    camera.start_recording(f'/home/pi/Desktop/Recordings/recording-{video_count}.h264')

    while True:

        # Checks if raspberry pi is overheating
        if overheating:
            if sense.get_cpu_temperature() >= max_temp:
                if not overheating:
                    camera.stop_recording()
                    video_count += 1
                    overheating = True
                continue
            else:
                camera.start_recording(f'/home/pi/Desktop/Recordings/recording-{video_count}.h264')
                overheating = False

        # Update display text (showing time, speed and temperature)
        camera.annotate_text = display_details(global_time, round(get_velocity(), 0), convert_temp(sense.get_temperature()))

        # Check if recording duration met
        if t == recording_duration:
            camera.stop_recording()

            video_count += 1
            camera.start_recording(f'/home/pi/Desktop/Recordings/recording-{video_count}.h264')
            t = 0

        sleep(1)
        global_time += 1
        t += 1


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
