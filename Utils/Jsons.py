import json as json_api
from typing import TypeVar, Callable

from requests_html import HTMLSession

from Regex import re_float
from Util import is_iter

T = TypeVar("T")
E = TypeVar("E")


def to_correct_json(string) -> str:
    return str(string).replace("True", "\"True\"").replace("False", "\"False\"").replace("'", "\"")
    # return str(string).replace("True", "\"True\"").replace("False", "\"False\"").replace("'", "\"").replace("\\",
    # "\\\\")


def text_to_json(json_text: str) -> dict[T, E]:
    return json_api.loads(to_correct_json(json_text))


def url_to_json(url: str) -> dict[T, E]:
    html_session = HTMLSession()
    html = html_session.get(url).text
    return text_to_json(html)


def url_to_json_ok(url: str,
                   keys: list[T] | T,
                   keys_start: list[T] = None,
                   condition: Callable[[dict[T, E]], bool] = None,
                   doublons=True) -> dict[T, E]:
    json = url_to_json(url)
    json_ok = json_to_json_ok(json, keys, keys_start, condition, doublons)
    if len(json_ok) == 0:
        raise ValueError("is not json")
    return json_ok


def json_to_json_ok(dictionaries: dict[T, E],
                    keys_aim: list[T],
                    keys_start: list[T] = None,
                    condition: Callable[[dict[T, E]], bool] = None,
                    doublons=True) -> dict[T, E]:
    """
    On remplace les indices de la liste de base en la transformant en un dictionnaire où les clefs seront les
    valeurs associés à la clef donné en paramètre des dictionnaires de la liste.
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


def text_to_json_ok(json_text: str,
                    keys: list[T] | T,
                    keys_start: list[T] = None,
                    condition: Callable[[dict[T, E]], bool] = None,
                    doublons=True) -> dict[T, E]:
    return json_to_json_ok(text_to_json(json_text), keys, keys_start, condition, doublons)


if __name__ == '__main__':
    # search value html
    asset = "waxp"
    nb_filter = "0.49"
    url = "https://coinmarketcap.com/fr/currencies/"
    print(url)
    html_session = HTMLSession()
    html = html_session.get('https://www.gate.io/fr/trade/{}_USDT'.format(asset)).text
    res = list(map(lambda x: x[0], filter(lambda n: nb_filter in n[0], re_float.findall(html))))
