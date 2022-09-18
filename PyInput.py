from pynput.keyboard import KeyCode, Listener

PYNPUT_DICT = {"keys_pressed": {}, "run": True}
NumpadDot = 110
_debug = False


def on_release(key: KeyCode):
    global _debug
    if _debug:
        PYNPUT_DICT["keys_pressed"][key] = False
    # print('{0} release'.format(key))


def on_press(key: KeyCode):
    global _debug
    if key in PYNPUT_DICT["keys_pressed"] and PYNPUT_DICT["keys_pressed"][key]:
        return
    if _debug:
        print('Key pressed: ' + str(key))
    PYNPUT_DICT["keys_pressed"][key] = True
    try:
        if key.vk == NumpadDot:
            PYNPUT_DICT["run"] = not PYNPUT_DICT["run"]
    except AttributeError:
        pass


def launch_keyboard_listener(debug=False, blocking=False):
    global _debug
    _debug = debug
    listener = Listener(on_press=on_press, on_release=on_release)
    listener.start()
    if blocking:
        listener.join()
