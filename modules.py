import shutil
from multiprocessing import Process
import utils

on_off = False
toggle_recording = False
clicks = 0
reading_button = False
total_holds = 0
releases = 0


def recording_icon(sense, is_recording):
    global on_off

    if not on_off or not is_recording:
        off = (0, 0, 0)
        sense.set_pixel(1, 1, off)
        sense.set_pixel(1, 2, off)
        sense.set_pixel(2, 1, off)
        sense.set_pixel(2, 2, off)
    else:
        red = (255, 0, 0)
        sense.set_pixel(1, 1, red)
        sense.set_pixel(1, 2, red)
        sense.set_pixel(2, 1, red)
        sense.set_pixel(2, 2, red)

    on_off = not on_off


def show_storage_usage(sense):
    total, used, free = shutil.disk_usage(f'/media/pi/{utils.get_drive_name()}/' if utils.use_drive else "/")
    perc_used = used / total

    if perc_used >= 0.75:
        status_color = (255, 0, 0)
    elif perc_used >= 0.50:
        status_color = (255, 100, 0)
    elif perc_used >= 0.25:
        status_color = (255, 255, 0)
    else:
        status_color = (0, 255, 0)

    div = 1.0 / 6.0
    test_num = perc_used / div
    status_limit = 1 + int(f'{test_num}'.split(".")[0])
    i = 0

    while i < status_limit:
        if i < 7:
            sense.set_pixel(1 + i, 6, status_color)

        i += 1


def handle_button(sense):
    global reading_button, clicks, total_holds, releases
    events = sense.stick.get_events()
    if len(events) == 0:
        if reading_button is True:
            reading_button = False
            total_holds = 0
            if clicks == 1:
                clicks = 0
                return 1
            elif clicks == 2:
                clicks = 0
                return 2
            clicks = 0
            releases = 0
            return 0
        else:
            return 0

    reading_button = True

    clicks += get_presses(events)
    total_holds += get_holds(events)
    releases += get_releases(events)

    if clicks >= 3:
        reading_button = 3
        clicks = 0
        total_holds = 0
        releases = 0
        return 3
    elif total_holds >= 3 and releases > 0:
        reading_button = 0
        clicks = 0
        total_holds = 0
        releases = 0
        return -1

    return 0


def get_presses(events):
    presses = 0

    for event in events:
        if event.action == "pressed":
            presses += 1

    return presses


def get_releases(events):
    releases = 0

    for event in events:
        if event.action == "released" and event.direction == "middle":
            releases += 1

    return releases


def get_holds(events):
    holds = 0

    for event in events:
        if event.action == "held":
            holds += 1

    return holds


def show_gps_status(sense):
    gps_is_set = utils.gpsd_is_set()
    print(gps_is_set, utils.gpsd.fix.speed)

    if gps_is_set:
        white = (255, 255, 255)
        no = (0, 0, 0)
        sense.set_pixel(4, 1, no)
        sense.set_pixel(6, 1, white)
        sense.set_pixel(5, 2, white)
        sense.set_pixel(6, 2, white)
        sense.set_pixel(4, 3, white)
        sense.set_pixel(5, 3, white)
        sense.set_pixel(6, 3, white)
    else:
        red = (255, 0, 0)
        no = (0, 0, 0)
        sense.set_pixel(4, 1, red)
        sense.set_pixel(6, 1, red)
        sense.set_pixel(5, 2, red)
        sense.set_pixel(6, 2, no)
        sense.set_pixel(4, 3, red)
        sense.set_pixel(5, 3, no)
        sense.set_pixel(6, 3, red)
