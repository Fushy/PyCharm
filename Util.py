import os
import string
from collections.abc import Iterable
from datetime import timedelta, datetime
from hashlib import blake2b
from time import sleep
from typing import Callable

import pandas as pd
import pyperclip
from pandas import DataFrame

from Times import now

# https://developer.microsoft.com/fr-fr/microsoft-edge/tools/webdriver/
# https://stackoverflow.com/questions/14684968/how-to-export-virtualenv
# pip install --upgrade pip
# pip install --upgrade setuptools
# pip install --upgrade pip setuptools
# pip install numpy
# pip install wheel
# pip install python-telegram-bot
# pip install python-telegram-bot --upgrade
# pip install python-telegram-bot
# pip install ffmpeg-python
# pip install pydub
# pip install selenium
# pip install msedge-selenium-tools
# pip install requests-html
# pip install http-request-randomizer
# pip install screeninfo
# pip install termcolor
# pip install gtts
# pip install simpleaudio
# pip install pyperclip
# pip install mysql-connector-python
# pip install gtts  https://ffmpeg.org/download.html#build-windows http://blog.gregzaal.com/how-to-install-ffmpeg-on-windows/
# pip install simpleaudio   sinon la lecture avec gtts n'est pas possible https://visualstudio.microsoft.com/visual-cpp-build-tools/
# if something is wrong
# https://www.lfd.uci.edu/~gohlke/pythonlibs/

# from util_bot import SEED_PATH_1, SEED_PATH_2

# def m(a, b):
#     pyperclip.copy((a + b) / 2)
#     return (a + b) / 2
#
#
# def a(a):
#     pyperclip.copy(a - 270)
#     return a - 270

COMMON_CHARS = (string.ascii_lowercase
                + string.ascii_uppercase
                + string.digits
                + "\ !#$%&()-@^_`{}~+,.;=[]\n")  # do not change "\ " it disables space character on command line


def restrict_num(x: float, _min: float, _max: float):
    if x < _min:
        x = _min
    if x > _max:
        x = _max
    return x


def reverse_dict(d: dict):
    return {tuple(v): k for (k, v) in d.items()}


def init_dataframe(columns) -> DataFrame:
    return pd.DataFrame({}.fromkeys(columns, []))


def add_rows_dataframe(df: DataFrame, rows: dict) -> DataFrame:
    """ slow, add all lines at the same time"""
    return pd.concat([df, pd.DataFrame(rows)]).drop_duplicates().reset_index(drop=True)


def add_columns_dataframe(df: DataFrame, columns: dict) -> DataFrame:
    """ slow, add all lines at the same time"""
    # np.set_printoptions(suppress=True,
    #                     formatter={'float_kind': '{:0.10f}'.date_format})
    for name, values in columns.items():
        df.insert(len(df.columns), name, values)
    return df


def auto_repr(cls):
    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, ', '.join('%s=%s' % item for item in vars(self).items()))

    cls.__repr__ = __repr__
    return cls


def computer_name():
    import platform
    return platform.node()


def get_pid():
    return os.getpid()


def is_docker() -> bool:
    import os
    return os.path.exists('/.dockerenv')


def get_os() -> str:
    import platform
    if platform.system() == 'Darwin':
        return 'mac'
    elif platform.system() == 'Linux':
        return 'linux'
    elif platform.system() == 'Windows':
        return 'windows'
    else:
        raise NotImplementedError(f'Unsupported OS: "{platform.system()}"')


def get_first_deeply_value(it: object):
    obj_val = it
    while isinstance(obj_val, Iterable):
        obj_val = obj_val[0]
    return obj_val


def str_to_hashcode(text: str or list[str], len_hashcode=8, seed=1337, whitelist="") -> list[str] or str:
    if whitelist == "":
        whitelist = string.ascii_letters + string.digits
    if is_iter(text):
        return [str_to_hashcode(txt, len_hashcode, seed, whitelist) for txt in text]
    encode = blake2b()
    if len_hashcode > encode.digest_size * 2 or len(str(seed)) >= 9:
        return ""
    encode.update(bytes(text.encode('utf-8')))
    hashcode = encode.hexdigest()
    hashtext = []
    part_len = (encode.digest_size * 2 // len_hashcode)
    for i in range(len_hashcode):
        txt = hashcode[i * part_len:(i + 1) * part_len]
        num = sum([(ord(c) * seed) for c in txt]) % len(whitelist)
        hashtext.append(whitelist[num])
    return "".join(hashtext)


def str_to_hashdigits(text, len_hashcode=32, seed=1337) -> int:
    whitelist = string.digits
    return int(str_to_hashcode(text, len_hashcode, seed, whitelist))


def datetime_to_timedelta(x):
    return x - datetime.strptime("0:0:0", "%H:%M:%S")


def is_iter(element):
    """ Si le type de l'objet peut être parcouru et n'est pas de type str"""
    if isinstance(element, Iterable) and not isinstance(element, str):
        return True
    return False


def know_connected_wifi_password():
    """netsh wlan show profiles "MAIS_MAROL" key = clear"""


def infinite_sequence():
    num = 0
    while True:
        num += 1
        yield num


def chained_list(*args):
    """ A utiliser lorsqu'il n'y pas d'effet de bord
    :param args:
    :return:
    """
    while True:
        for element in args:
            yield element


def selenium_screenshot(browser, file=""):
    if file == "":
        file = now().strftime("%d-%m-%y %H-%M-%S %Z")
    # save_browser = copy.deepcopy(browser)
    save_browser = browser
    print("screenshot", now().strftime("%d-%m-%y %H-%M-%S %Z"))
    for i in range(len(save_browser.window_handles)):
        save_browser.switch_to.window(save_browser.window_handles[i])
        print("\tscreenshots\\" + file + "_" + str(i) + ".png")
        save_browser.get_screenshot_as_file("screenshots\\" + file + "_" + str(i) + ".png")


def debug_selenium(browser):
    while True:
        selenium_screenshot(browser)
        sleep(0.5)


def sorted_dict(dictionary: dict, key=lambda x: x, reverse=False) -> dict:
    return dict(sorted(dictionary.items(), key=key, reverse=reverse))


def sorted_dict_str(dictionary: dict, key=lambda x: x, reverse=False) -> str:
    result = "{"
    v_is_dict = False
    for k, v in sorted(dictionary.items(), key=key, reverse=reverse):
        if type(v) is dict:
            v_is_dict = True
            v = sorted_dict(v)
        elif type(v) is Iterable:
            v = sorted(v)
        k = str(k)
        if v_is_dict is False:
            v = str(v)
            if v.isalnum() or v.isalpha() or v.isidentifier() or v.isascii():
                result += "\"" + k + "\":\"" + v + "\","
            else:
                result += "\"" + k + "\":" + v + ","
        else:
            v = str(v)
            if v.isalnum() or v.isalpha() or v.isidentifier():
                result += "\"" + k + "\":\"" + v + "\","
            else:
                result += "\"" + k + "\":" + v + ","
    result = list(result)
    result[-1:] = "}"
    return "".join(result)


def repeat_function_binance(fun: Callable, interval_time: timedelta, debug=False, *args):
    """ Une fois que la fonction est terminée, on attend :interval_time:."""
    while True:
        fun()
        if debug:
            print(now().strftime("%Y-%m-%d %H:%M:%S"), "executed successfully", *args)
        sleep(interval_time.total_seconds())


def action_on_clipboard_update(fun: Callable):
    old_clipboard = ""
    while True:
        clipboard = pyperclip.paste()
        if clipboard != old_clipboard:
            fun(clipboard)
        old_clipboard = clipboard
        sleep(0.5)


def two_complement_representation(x: int):
    mask = 2 ** (8 * ((x.bit_length() // 8) + 1)) - 1
    return x & mask


def two_complement_representation_2(x: int):
    shift = 8 * ((x.bit_length() // 8) + 1)
    return x % (1 << shift)


def two_complement_representation_3(x: int):
    from ctypes import c_uint8 as unsigned_byte
    return unsigned_byte(x).value

# if __name__ == '__main__':
#     seed = int(str_to_hashcode(file_get_1st_line(SEED_PATH_1) + file_get_1st_line(SEED_PATH_2), whitelist=string.digits))
#     a = ["b4nvi.wam",
#          "pyyfu.wam",
#          "progk.wam",
#          "o.gvy.wam",
#          "xvzwu.wam",
#          "n11k2.c.wam",
#          "jd1.2.c.wam",
#          "g32ke.c.wam",
#          "e33ke.c.wam",
#          "oj3.e.c.wam"]
#     print(a[0], str_to_hashcode(a[0], seed=seed))
#     print(list(zip(a, str_to_hashcode(a, seed=seed))))
