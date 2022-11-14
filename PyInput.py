from typing import Callable

from pynput.keyboard import KeyCode, Listener, Key

_debug = False
PYNPUT_DICT = {"keys_pressed": {}, "run": True}
NumpadDot = 110
NumpadMult = 106
NumpadAdd = 107
Ctrl = Key.ctrl_l
Alt = Key.alt_l
Win = Key.cmd
Shift = Key.shift
Backspace = Key.backspace
Escape = Key.esc
Space = Key.space


def on_release(key: KeyCode):
    global _debug
    PYNPUT_DICT["keys_pressed"][key] = False
    if _debug:
        print('|{} release|'.format(key))


def on_press(key: KeyCode):
    """ NumpadDot par defaut qui control le le flux du thread """
    global _debug
    if key in PYNPUT_DICT["keys_pressed"] and PYNPUT_DICT["keys_pressed"][key]:
        return
    PYNPUT_DICT["keys_pressed"][key] = True
    try:
        # _debug = True
        if _debug:
            try:
                print("|Key pressed:{}|".format(key), end=" ")
                print("|vk:{}|".format(key.vk), end=" ")
            except AttributeError:
                print("|no vk|", end=" ")
        # if key == Key.pause:
        if key.vk == NumpadDot:
            PYNPUT_DICT["run"] = not PYNPUT_DICT["run"]
    except AttributeError:
        pass


def on_press_skeleton(key: KeyCode):
    if key in PYNPUT_DICT["keys_pressed"] and PYNPUT_DICT["keys_pressed"][key]:
        return
    PYNPUT_DICT["keys_pressed"][key] = True


def launch_keyboard_listener(press: Callable = on_press, release: Callable = on_release, debug=False, blocking=False):
    global _debug
    _debug = debug
    listener = Listener(on_press=press, on_release=release)
    listener.start()
    if blocking:
        listener.join()

def eq(key: KeyCode, value: KeyCode | str | int):
    try:
        if key == value or key.char == value or key.vk == value:
            return True
    except AttributeError:
        pass
    return False


if __name__ == '__main__':
    launch_keyboard_listener(debug=True, blocking=True)
