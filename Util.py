import itertools
import string
from collections.abc import Iterable
from datetime import timedelta, datetime
from hashlib import blake2b
from time import sleep
from typing import Callable

import pyperclip

from Files import file_get_1st_line
from Times import now
# https://stackoverflow.com/questions/14684968/how-to-export-virtualenv
# pip install --upgrade
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
from util_bot import SEED_PATH_1, SEED_PATH_2


def str_to_hashcode(text: str | list[str], len_hashcode=8, seed=1337, whitelist="") -> list[str] | str:
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
    for i in range(len_hashcode):
        txt = hashcode[i * (encode.digest_size * 2 // len_hashcode):(i + 1) * (encode.digest_size * 2 // len_hashcode)]
        num = sum([(ord(c) << seed) * seed for c in txt]) % len(whitelist)
        hashtext.append(whitelist[num])
    return "".join(hashtext)


def datetime_to_timedelta(x):
    return x - datetime.strptime("0:0:0", "%H:%M:%S")


def is_iter(element):
    """ Si le type de l'objet peut être parcouru et n'est pas de type str"""
    if isinstance(element, Iterable) and not isinstance(element, str):
        return True
    return False


def know_connected_wifi_password():
    """netsh wlan show profiles "MAIS_MAROL" key = clear"""


def permutations(elements):
    return list(itertools.permutations(elements))


def all_permutations(elements):
    return [set(itertools.permutations(elements, i)) for i in range(len(elements))]


def infinite_sequence():
    num = 0
    while True:
        num += 1
        yield num


def chained_list(*args):
    """ A utiliser lorsqu'il n'y a pas d'effet de bord
    :param args:
    :return:
    """
    while True:
        for element in args:
            yield element


def loop_screenshot(browser):
    while True:
        screenshot(browser)
        sleep(0.1)


def screenshot(browser, file=""):
    if file == "":
        file = now().strftime("%d-%m-%y %H-%M-%S %Z")
    # save_browser = copy.deepcopy(browser)
    save_browser = browser
    print("screenshot", now().strftime("%d-%m-%y %H-%M-%S %Z"))
    for i in range(len(save_browser.window_handles)):
        save_browser.switch_to.window(save_browser.window_handles[i])
        print("\tscreenshots\\" + file + "_" + str(i) + ".png")
        save_browser.get_screenshot_as_file("screenshots\\" + file + "_" + str(i) + ".png")


def util_action_on_one_clipboard_change(fun: Callable):
    old_clipboard = ""
    while True:
        clipboard = pyperclip.paste()
        if clipboard != old_clipboard:
            fun(clipboard)
        old_clipboard = clipboard
        sleep(1)


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


def util_repeat_function_binance(fun: Callable, interval_time: timedelta, debug=False, *args):
    """ Une fois que la fonction est terminée, on attend :interval_time:."""
    while True:
        fun()
        if debug:
            print(now().strftime("%Y-%m-%d %H:%M:%S"), "executed successfully", *args)
        sleep(interval_time.total_seconds())


# def set_bag_alienworlds(browser, tool_name):
#     """ Doit  au préalable être connecté """
#     left_interface_xpath = "/html/body/div/div[3]/div[1]/div/div[2]/button"
#     wait_n_click(browser, left_interface_xpath)
#     switch_tools_xpath = "/html/body/div/div[3]/div[2]/div[1]/div/div/div[2]/div/div/div[1]/div[2]/button"
#     wait_n_click(browser, switch_tools_xpath)
#     sleep(1)
#     tools_xpath = list(
#         "/html/body/div/div[3]/div[2]/div[2]/div/div/div/div/div/div[3]/div[2]/div[{}]".format(i) for i in range(1,
#         4))
#     tools = list(map(lambda x: get_element(browser, x), tools_xpath))
#     last_tool = get_element(browser, "/html/body/div/div[3]/div[2]/div[2]/div/div/div/div/div/div[3]/div[2]/div[3]")
#     while last_tool:
#         advenced_tds = get_all_tag_that_contains(last_tool, [lambda x: tool_name == x], alone=True)
#         if advenced_tds is None or len(advenced_tds) != 0:
#             break
#         else:
#             element_click(browser, last_tool)
#         advenced_tds = get_all_tag_that_contains(last_tool, [lambda x: tool_name == x], alone=True)
#         if advenced_tds is None or len(advenced_tds) == 0:
#             continue
#         element_click(browser, advenced_tds[tool_name])
#         check_wax_approve(browser)
#         sleep(1)
#         last_tool = get_element(browser, "/html/body/div/div[3]/div[2]/div[2]/div/div/div/div/div/div[3]/div[
#         2]/div[3]")
#     return True
#
#
# def set_bag_waxblocks(browser, to, ids: list[int]):
#     try:
#         print("set_bag", to, ids)
#         if not whitelist_wam_account(to):
#             raise ValueError("Wam account is not whitelisted")
#         search_account_input_xpath = "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div[1]/div/div/form/div/input"
#         search_account_input = get_element(browser, search_account_input_xpath)
#         account_name = "m.federation"
#         waxblocks_connection(browser, False)
#         clear_send(search_account_input)
#         element_send(search_account_input, account_name, Keys.ENTER)
#         contract_tab_xpath = "/html/body/div[1]/div[2]/div/div[1]/div[2]/div[2]"
#         if not wait_n_click(browser, contract_tab_xpath):
#             say("change VPN connection")
#             return False
#         action_tab_xpath = "/html/body/div[1]/div[2]/div/div[2]/div[3]/div/div[3]/div[2]"
#         if not wait_n_click(browser, action_tab_xpath):
#             say("change VPN connection")
#             return False
#         setbag_onglet_xpath = "/html/body/div[1]/div[2]/div/div[2]/div[3]/div/div[4]/div/div/div/div/div/span[17]"
#         if not wait_n_click(browser, setbag_onglet_xpath):
#             say("change VPN connection")
#             return False
#         to_account_xpath = "/html/body/div[1]/div[2]/div/div[2]/div[3]/div/div[4]/div/div/div/div[2]/div/div[
#         1]/div/div/input"
#         to_account = get_element(browser, to_account_xpath)
#         clear_send(to_account)
#         element_send(to_account, to, Keys.TAB, "[" + ",".join(map(str, ids)) + "]")
#         sleep(1)
#         submit_xpath = "/html/body/div[1]/div[2]/div/div[2]/div[3]/div/div[4]/div/div/div/div[2]/button"
#         if not wait_n_click(browser, submit_xpath):
#             say("change VPN connection")
#             return False
#         sleep(5)
#         if not check_wax_approve(browser):
#             close_current_and_go_home(browser)
#             return True
#         message_transaction_xpath = "/html/body/div[1]/div[2]/div/div[2]/div[3]/div/div[4]/div/div/div/div[3]/div"
#         if not wait_element(browser, message_transaction_xpath, leave=10):
#             return False
#         message_transaction_text = get_text(browser, message_transaction_xpath)
#         print("\tmessage set_bag", message_transaction_text)
#         if "Error" == message_transaction_text:
#             return False
#         return True
#     except StaleElementReferenceException:
#         return set_bag_waxblocks(browser, to, ids)
#
#

if __name__ == '__main__':
    seed = int(str_to_hashcode(file_get_1st_line(SEED_PATH_1) + file_get_1st_line(SEED_PATH_2), whitelist=string.digits))
    a = ["b4nvi.wam",
         "pyyfu.wam",
         "progk.wam",
         "o.gvy.wam",
         "xvzwu.wam",
         "n11k2.c.wam",
         "jd1.2.c.wam",
         "g32ke.c.wam",
         "e33ke.c.wam",
         "oj3.e.c.wam"]
    print(a[0], str_to_hashcode(a[0], seed=seed))
    print(list(zip(a, str_to_hashcode(a, seed=seed))))
