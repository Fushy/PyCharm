from asyncio import sleep

import pyautogui
import win32gui

from Classes import Point
from Times import now, elapsed_seconds


def click(x: int | Point | None = None, y=None):
    if x is None:
        pyautogui.click()
        return
    if type(x) is Point:
        y = x.y
        x = x.x
    pyautogui.click(x=x, y=y)


def move(x: int | Point, y=None):
    if type(x) is Point:
        y = x.y
        x = x.x
    pyautogui.moveTo(x=x, y=y)


def click_n_rewind(x: int | Point | None, y=None):
    save_pos = mouse_get_pos()
    # move(x, y)
    click(x, y)
    move(save_pos)


def send(*keys, press_time=0.1):
    # https://pyautogui.readthedocs.io/en/latest/keyboard.html#keyboard-keys
    for key in keys:
        if not press_time:
            pyautogui.press(key)
        else:
            pyautogui.keyDown(key)
            sleep(press_time)
            pyautogui.keyUp(key)


def mouse_get_pos() -> Point:
    flags, hcursor, (x, y) = win32gui.GetCursorInfo()
    return Point(x, y)


def win_get_active_title() -> str:
    return win32gui.GetWindowText(win32gui.GetForegroundWindow())


if __name__ == '__main__':
    pass
