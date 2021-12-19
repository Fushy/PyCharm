import json as json_api
from typing import TypeVar

T = TypeVar("T")
E = TypeVar("E")


def to_correct_json(string) -> str:
    return str(string).replace("True", "\"True\"").replace("False", "\"False\"").replace("'", "\"")
    # return str(string).replace("True", "\"True\"").replace("False", "\"False\"").replace("'", "\"").replace("\\", "\\\\")


def json_to_obj(json: object):
    return json_api.loads(to_correct_json(json))


def improve_dict(dictionaries: list[dict[T, E]], key: T) -> dict[T, E]:
    """
    On remplace les indices de la liste de base en la transformant en un dictionnaire où les clefs seront les
    valeurs associés à la clef donné en paramètre des dictionnaires de la liste.
    """
    result = {}
    for dictionary in dictionaries:
        result[dictionary[key]] = dictionary
    return result


def json_to_improve_dict(json: object, key: T = None) -> dict[T, E]:
    return improve_dict(json_to_obj(json), key)
