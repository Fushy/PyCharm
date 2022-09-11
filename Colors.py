from termcolor import colored

from denombrement import permutations_all_size


def printc(text: str, color="green", background_color=None, attributes: list[str] = None, details=False):
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
    print(colored("{} {}".format(text, details_txt),
                  color,
                  "on_" + background_color if background_color is not None else None,
                  attrs=attributes))


def print_all_colors():
    colors = ["red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    # attributes = ["bold", "underline", "reverse"]
    attributes = ["bold", "underline"]
    for perms_same_len in permutations_all_size(attributes):
        for perms in perms_same_len:
            for c in colors:
                printc("Hello, World! attributes={} color={}".format(list(perms), c), color=c, attributes=perms)
                printc("Hello, World! attributes={} color={}".format(list(perms + ("reverse",)), c), color=c, attributes=perms + ("reverse",))
                # for cc in colors:
                #     printc("Hello, World! perms={} color={} background_color={}".format(perms, cc, c),
                #            color=cc,
                #            background_color=c,
                #            attributes=perms)


if __name__ == '__main__':
    print_all_colors()
