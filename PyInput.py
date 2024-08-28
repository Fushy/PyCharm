from collections import defaultdict
from time import sleep
from typing import Callable
import keyboard
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
        "alt+h": 72,
        "alt+j": 74,
        }


def on_release(key: KeyCode):
    global _debug
    # print("_________", key)
    key_v = key_value(key)
    PYNPUT_DICT["keys_pressed"][key_v] = False
    if _debug:
        try:
            if key.char is None:
                raise AttributeError
            print("Key released: char |{}|".format(repr(key.char)), end=" ")
        except AttributeError:
            try:
                print("Key released: vk |{}|".format(key.vk), end=" ")
            except AttributeError:
                print("Key released: ", key, "|no char no vk|", end=" ")
        print(list(PYNPUT_DICT["keys_pressed"].items()))
        print()


def on_press(key: KeyCode, debug=None):
    """ NumpadDot par defaut qui control le flux du thread
        Quand on parse les keys, toujours mettre les key.vk en fin de if statement """
    global _debug
    if debug is not None:
        _debug = debug
    key_v = key_value(key)
    if key_v in PYNPUT_DICT["keys_pressed"] and PYNPUT_DICT["keys_pressed"][key_v]:
        return
    PYNPUT_DICT["keys_pressed"][key_v] = True
    try:
        # if key == Key.pause:
        if key.vk == NumpadDot:
            PYNPUT_DICT["run"] = not PYNPUT_DICT["run"]
    except AttributeError:
        pass
    if _debug:
        print(list(PYNPUT_DICT["keys_pressed"].items()))


def on_press_skeleton(key: KeyCode):
    key_v = key_value(key)
    if key_v in PYNPUT_DICT["keys_pressed"] and PYNPUT_DICT["keys_pressed"][key_v]:
        return
    PYNPUT_DICT["keys_pressed"][key_v] = True


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


def key_value(key: KeyCode, debug=False) -> str | int | KeyCode:
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
    print("start")
    # launch_keyboard_listener(debug=True, blocking=True)
    launch_keyboard_listener(debug=True, blocking=False)
    while True:
        sleep(0.1)
    # while not PYNPUT_DICT["keys_pressed"][Ctrl["v"]]:
    #     sleep(0.1)
    #     print("wait")