from collections import defaultdict
from typing import Callable

from pynput.keyboard import KeyCode, Listener, Key

_debug = False
PYNPUT_DICT = {"keys_pressed": defaultdict(lambda: False, {}), "run": True}
NumpadDot = 110
NumpadMult = 106
NumpadAdd = 107
Alt = Key.alt_l
Win = Key.cmd
Shift = Key.shift
Backspace = Key.backspace
Escape = Key.esc
Space = Key.space
Ctrl = {"": Key.ctrl_l,
        "&": 49,
        "a": "'\\x01'",
        "v": "'\\x16'",
        "alt+a": 65,
        "alt+v": 86,
}


def on_release(key: KeyCode):
    global _debug
    PYNPUT_DICT["keys_pressed"][key] = False
    if _debug:
        try:
            if key.char is None:
                raise AttributeError
            print("Key released:char |{}|".format(repr(key.char)), end=" ")
        except AttributeError:
            try:
                print("Key released: vk |{}|".format(key.vk), end=" ")
            except AttributeError:
                print(key, "|no char no vk| released", end=" ")
        print()


def on_press(key: KeyCode):
    """ NumpadDot par defaut qui control le flux du thread """
    global _debug
    if key in PYNPUT_DICT["keys_pressed"] and PYNPUT_DICT["keys_pressed"][key]:
        return
    PYNPUT_DICT["keys_pressed"][key] = True
    try:
        first_value(key, debug=True)
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

def first_value(key: KeyCode, debug=False) -> str | int | KeyCode:
    try:
        if key.char is None:
            raise AttributeError
        if debug:
            print("Key pressed:char |{}|".format(repr(key.char)), end=" ")  # repr for printing ctrl+key
        return repr(key.char)
    except AttributeError:
        try:
            if debug:
                print("Key pressed: vk |{}|".format(key.vk), end=" ")
            return key.vk
        except AttributeError:
            if debug:
                print(key, "|no char no vk| pressed", end=" ")
            return key


if __name__ == '__main__':
    launch_keyboard_listener(debug=True, blocking=True)
