from asyncio import sleep
import os

import pyautogui
import win32gui

from Classes import Point


def launch_ahk_text(text, base=None, file_name="temp.ahk"):
    base = """
            if not A_IsAdmin
              Run *RunAs "%A_ScriptFullPath%"
            if not A_IsAdmin
              ExitApp
            CoordMode, Pixel, Screen
            CoordMode, Mouse, Screen
            CoordMode, ToolTip, Screen
            SetTitleMatchMode, 1
            SetBatchLines, -1
            DetectHiddenWindows, On
            SetKeyDelay, 50
            """ if base is None else base
    ahk_text = base + text
    with open(file_name, 'w', encoding="utf-8") as f:
        f.write(ahk_text)
    os.system(file_name)


def click(x: int | Point | None = None, y=None, ahk=False, file_name="click.ahk"):
    if type(x) is Point:
        y = x.y
        x = x.x
    if not ahk:
        if x is None:
            pyautogui.click()
            return
        pyautogui.click(x=x, y=y)
    else:
        launch_ahk_text("""
        lParam := {}
        SendMessage, 0x201, 0x00000000, lParam,, A
        SendMessage, 0x202, 0x00000000, lParam,, A""".format(0 if x is None else (y << 16) | x), file_name=file_name)


def mouse_move(x: int | Point, y=None, ahk=False, title="A", file_name="mouse_move_vars.ahk"):
    if type(x) is Point:
        y = x.y
        x = x.x
    if not ahk:
        pyautogui.moveTo(x=x, y=y)
    else:
        launch_ahk_text("""
        winactivate, Program Manager
        mousegetpos, mx, my
        tooltip, a, mx-10, my-10
        mousemove, {}, {}, 0
        tooltip
        winactivate, {}""".format(x, y, title), file_name=file_name)


def mouse_click_ahk(x, y, title="A", file_name="mouse_click_ahk.ahk"):
    launch_ahk_text("""
        winactivate, Program Manager
        mousegetpos, mx, my
        tooltip, a, mx-10, my-10
        mousemove, {}, {}, 0
        tooltip
        winactivate, {}
        SendMessage, 0x201,,,, A
        SendMessage, 0x202,,,, A
        winactivate, Program Manager
        mousegetpos, mxx, myy
        tooltip, a, mxx-10, myy-10
        mousemove, mx, my, 0
        tooltip
        winactivate, {}""".format(x, y, title, title), file_name=file_name)


def click_n_rewind(x: int | Point | None, y=None):
    save_pos = mouse_get_pos()
    # move(x, y)
    click(x, y)
    mouse_move(save_pos)


def send(keys: list | str, press_time=0.1, ahk=False):
    # https://pyautogui.readthedocs.io/en/latest/keyboard.html#keyboard-keys
    if not ahk:
        for key in keys:
            if not press_time:
                pyautogui.press(key)
            else:
                pyautogui.keyDown(key)
                sleep(press_time)
                pyautogui.keyUp(key)
    elif ahk:
        for key in keys:
            launch_ahk_text("""
            SendMessage, 0x0102, {}, 0x01f0010f,,A ; Char
            SendMessage, 0x0100, {}, 0x01f0010f,,A ; Down
            sleep, {}
            SendMessage, 0x0101, {}, 0x01f0010f,,A ; Up""".format(ord(key), ord(key), press_time, ord(key)))



def mouse_get_pos() -> Point:
    flags, hcursor, (x, y) = win32gui.GetCursorInfo()
    return Point(x, y)


def win_get_active_title() -> str:
    return win32gui.GetWindowText(win32gui.GetForegroundWindow())


if __name__ == '__main__':
    pass
