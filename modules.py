import shutil

on_off = False

def recording_icon(sense, is_recording):
    global on_off

    if not on_off or not is_recording:
        off = (0, 0, 0)
        sense.set(1, 1, off)
        sense.set(1, 2, off)
        sense.set(2, 1, off)
        sense.set(2, 2, off)
    else:
        red = (255, 0, 0)
        sense.set(1, 1, red)
        sense.set(1, 2, red)
        sense.set(2, 1, red)
        sense.set(2, 2, red)

    on_off = not on_off

def show_storage_usage(sense):
