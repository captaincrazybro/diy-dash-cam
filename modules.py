import shutil
from multiprocessing import Process
import utils

on_off = False
toggle_recording = False
clicks = 0
reading_button = False
total_holds = 0


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
    total, used, free = shutil.disk_usage("/")
    perc_used = used / total

    if perc_used >= 0.25:
        status_color = (255, 0, 0)
    elif perc_used >= 0.50:
        status_color = (255, 255, 0)
    elif perc_used >= 0.75:
        status_color = (255, 165, 0)
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
    global reading_button, clicks, total_holds
    events = sense.stick.get_events()
    if len(events) == 0:
        if reading_button is True:
            reading_button = False
            total_holds = 0
            if clicks == 1:
                clicks = 0
                return True
            elif clicks == 2:
                clicks = 0
                utils.transfer_files(transfer_all=False)
                return False
            clicks = 0
        else:
            return False

    reading_button = True

    print(events)
    presses = get_presses(events)
    holds = get_holds(events)

    clicks += presses
    total_holds += holds

    if clicks >= 3:
        reading_button = False
        clicks = 0
        total_holds = 0
        utils.transfer_files(transfer_all=True)
    elif total_holds >= 3:
        reading_button = False
        clicks = 0
        total_holds = 0
        print("HOLD CLICK")

    return False


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
