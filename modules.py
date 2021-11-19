import shutil

on_off = False


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
