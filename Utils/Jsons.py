import json
import json as json_api
import socket
from time import sleep
from typing import TypeVar, Callable, Optional

import requests
from requests.exceptions import ChunkedEncodingError, SSLError
from requests_html import HTMLSession
from urllib3.exceptions import NewConnectionError, MaxRetryError

from Colors import printc
from Times import now, elapsed_minutes

T = TypeVar("T")
E = TypeVar("E")
json_T = dict[T, E]


def to_correct_json(string) -> str:
    return str(string).replace("True", "\"True\"").replace("False", "\"False\"").replace("'", "\"")
    # return str(string).replace("True", "\"True\"").replace("False", "\"False\"").replace("'", "\"").replace("\\",
    # "\\\\")


def text_to_json(json_text: str) -> json_T:
    return json_api.loads(to_correct_json(json_text))


def url_to_json(url: str) -> Optional[json_T]:
    html_session = HTMLSession()
    try:
        start = now()
        while True:
            try:
                if elapsed_minutes(start) >= 1:
                    return None
                html_result_text = html_session.get(url)
                html_result_text = html_result_text.text
            except ChunkedEncodingError or ConnectionError or NewConnectionError or socket.gaierror \
                   or json.decoder.JSONDecodeError or requests.exceptions.ConnectTimeout:
                printc("url_to_json ChunkedEncodingError", background_color="red")
                sleep(2)
                return url_to_json(url)
            if "503 Service Unavailable" in html_result_text or "<Response [403]>" in html_result_text:
                print("url_to_json error: err Response in html_result_text")
                sleep(5)
            elif is_json(html_result_text):
                break
        return text_to_json(html_result_text)
    except MaxRetryError or SSLError:
        return None


def call_request_api(base_urls: list[str], *start_with, parameters_n_values=None):
    args = ""
    if parameters_n_values is not None:
        args = "&".join((arg + "=" + value for (arg, value) in list(parameters_n_values.items()) if value is not None))
    api_call_url = ""
    for api_call_url in base_urls:
        # try:
        api_call_url += "/" + "/".join(start_with)
        if parameters_n_values is not None:
            api_call_url += "?{}".format(args)
        # except:
        #     continue
        break
    print(api_call_url)
    all_asset_price = url_to_json(api_call_url)
    return all_asset_price


def is_json(txt):
    try:
        json_api.loads(to_correct_json(txt))
        return True
    except:
        return False


def json_to_json_ok(dictionaries: json_T,
                    keys_aim: list[T],
                    keys_start: list[T] = None,
                    condition: Callable[[json_T], bool] = None,
                    doublons=True) -> json_T:
    """
    On remplace les indices de la liste de base en la transformant en un dictionnaire où
    les clefs seront les valeurs associés à la clef donné en paramètre des dictionnaires de la liste
    Si il y a plusieurs keys, tous les champs doivent avoir le même pattern
    """
    result = {}
    if keys_start is not None:
        for key in keys_start:
            dictionaries = dictionaries[key]
    for dictionary in dictionaries:
        key_cursor = dictionary
        for k in keys_aim[:-1]:
            key_cursor = key_cursor[k]
        key = key_cursor[keys_aim[-1]]
        if condition is not None and not condition(dictionary):
            continue
        if doublons and key in result:
            if type(result[key]) is not list:
                result[key] = [result[key]]
            result[key].append(dictionary)
        else:
            result[key] = dictionary
    return result


def url_to_json_ok(url: str,
                   keys: list[T],
                   keys_start: list[T] = None,
                   condition: Callable[[json_T], bool] = None,
                   doublons=True) -> Optional[json_T]:
    json = url_to_json(url)
    if json is None:
        return None
    json_ok = json_to_json_ok(json, keys, keys_start, condition, doublons)
    if len(json_ok) == 0:
        raise ValueError("is not json")
    return json_ok


def text_to_json_ok(json_text: str,
                    keys: list[T] | T,
                    keys_start: list[T] = None,
                    condition: Callable[[json_T], bool] = None,
                    doublons=True) -> json_T:
    return json_to_json_ok(text_to_json(json_text), keys, keys_start, condition, doublons)


if __name__ == '__main__':
    asset_amount = call_request_api(["https://wax.light-api.net/api"], "account", "wax", "b4nvi.wam")
    asset_amount = json_to_json_ok(asset_amount, ["currency"], ["balances"])
