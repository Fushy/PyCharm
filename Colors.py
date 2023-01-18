from time import sleep
from typing import Iterable

from colorama import init, Fore, Style, Back
from termcolor import colored

from Threads import run
from Times import now, elapsed_seconds
from Util import is_running_under_basic_console
from denombrement import permutations_all_size


def printt(text: str, color="green", background_color=None, attributes: Iterable[str] = None, details=False):
    """ It works on PyCharm
        color & background_color: red, green, yellow, blue, magenta, cyan, white, black
        attributes: bold, dark, underline, blink, reverse, concealed
        pycharm attributes: bold, underline, reverse
    """
    if color == "black":
        color = "grey"
    if background_color == "black":
        background_color = "grey"
    details_txt = ""
    if details:
        details_txt = "[{} {}]".format(color, attributes)
    if not is_running_under_basic_console():
        txt = colored("{} {}".format(text, details_txt),
                      color,
                      "on_" + background_color if background_color is not None else None,
                      attrs=attributes)
    else:
        txt = "{} {}".format(text, details_txt)
    print(txt)


def printc(text: str, color="green", background_color=None, attributes: Iterable[str] = ["NORMAL"]):
    """ It works on PyCharm but bug after 250 use with the option "Emulate terminal in output control"
        color & background_color: red, green, yellow, blue, magenta, cyan, white, black
        attributes: bold, dark, underline, blink, reverse, concealed
        pycharm attributes: bold, underline, reverse
    """
    init()
    style = getattr(Fore, color.upper()) if color != "" else ""
    if background_color is not None:
        style += getattr(Back, background_color.upper())
    if attributes:
        " ".join([getattr(Style, attribute.upper()) for attribute in attributes])
    print("{}{}{}".format(style, text, Style.RESET_ALL))


def print_all_colors_colorama():
    init()
    colors = ["RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE", "BLACK", ""]
    attributes = ["NORMAL", "BRIGHT", "DIM"]
    for attribute in attributes:
        for c in colors:
            printc("Hello, World! color={} attributes={}".format(c, attribute), color=c, attributes=[attribute])
            printc("Hello, World! color={} background=black attributes={}".format(c, attribute),
                   color=c, background_color="black", attributes=[attribute])
            # for background in colors:
            #     printc("Hello, World! color={} background={} attributes={}".format(c, background, attribute),
            #            color=c, background_color=background, attributes=[attribute])


def print_all_colors_termcolor():
    colors = ["red", "green", "yellow", "blue", "magenta", "cyan", "white", ""]
    # attributes = ["bold", "underline", "reverse"]
    attributes = ["bold", "underline"]
    for perms_same_len in permutations_all_size(attributes):
        for perms in perms_same_len:
            perms = tuple(perms)
            for c in colors:
                printt("Hello, World! attributes={} color={}".format(perms, c), color=c, attributes=perms)
                printt("Hello, World! attributes={} color={}".format(perms + ("reverse",), c), color=c,
                       attributes=perms + ("reverse",))
                # for cc in colors:
                #     printc("Hello, World! perms={} color={} background_color={}".format(perms, cc, c),
                #            color=cc,
                #            background_color=c,
                #            attributes=perms)


if __name__ == '__main__':
    # while True:
    print_all_colors_colorama()
    # print_all_colors_termcolor()
    # printc("Hello, World!", color="black", background_color="blue", attributes=["dim"])
    # printc("Hello, World!", color="black")
    # input()
