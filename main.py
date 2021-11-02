from picamera import PiCamera
from time import sleep

def main():
    camera = PiCamera()

    camera.start_preview()
    camera.start_recording('/home/pi/Desktop/video.h264')
    camera.annotate_text = "Hello ther!"
    sleep(5)
    camera.stop_recording()
    camera.stop_preview()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
