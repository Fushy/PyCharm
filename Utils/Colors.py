from termcolor import colored

from Util import all_permutations, permutations


def printc(text: str, color="green", background_color=None, attributes: list[str] = None):
    """
        color & background_color: red, green, yellow, blue, magenta, cyan, white, black
        attributes: bold, dark, underline, blink, reverse, concealed
        pycharm attributes: bold, underline, reverse
    """
    if color == "black":
        color = "grey"
    if background_color == "black":
        background_color = "grey"
    print(colored("{} [{} {}]".format(text, color, attributes),
                  color,
                  "on_" + background_color if background_color is not None else None,
                  attrs=attributes))


if __name__ == '__main__':
    # TODO get combinaison file
    # colors = ["red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    # attributes = ["bold", "underline", "reverse"]
    # for perms_same_len in all_permutations(attributes):
    #     for perms in perms_same_len:
    #         printc('Hello, World! {}'.format(perms), attributes=perms)
    # for perms_same_len in all_permutations(attributes):
    #     for perms in perms_same_len:
    #         printc('Hello, World! {}'.format(perms), background_color="red", attributes=perms)
    # print('')
    txt = r"	progk next_run ¤ 2021-12-31 18:50:09.114839 ¤ delta ¤ 0:01:37.601905 ¤ pause_time ¤ 0:00:30.601905 ¤ [1, 'pyyfu', 240, [1099533713249, 1099536734025, 1099546576702], '2022-01-01 04:30:18.184906']			progk ['https://alienworlds.io/', 'https://play.alienworlds.io/inventory'] Monitor(x=-11.0, y=2592.0, width=1920, height=1080, width_mm=None, height_mm=None, name='hide', is_primary=False) user-data-dir=C:\Users\alexi_mcstqby\Documents\Bots\AlienWorlds\Profiles\progk"
    # txt = 'Hello, World!'
    printc(txt, color="red")
    printc(txt, background_color="red")
    printc(txt, color="blue", background_color="red")
    printc(txt, attributes=["bold"])
    printc(txt, color="blue", attributes=["bold"])
    printc(txt, background_color="red", attributes=["bold"])
    printc(txt, color="grey", background_color="red", attributes=["bold"])
