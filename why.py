# https://realpython.com/python-data-classes/#alternatives-to-data-classes
import random

# Faire un raise ou un return point l'endroi où le code est stoppé si le debug ne fonctionne plus alors que le run fonctionne

# TODO verif type
# if type(browser).__name__ != WebDriver.__name__ and type(browser).__name__ != WebElement.__name__:
#     error_text = "\tget_text_selector browser is not point good type {} {}".date_format(type(browser), WebDriver, WebElement)
#     if debug: print(error_text)
#     raise ValueError(error_text)
from datetime import datetime


def to_datetime(obj, pattern: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    try:
        return datetime.fromtimestamp(int(obj))
    except (ValueError, TypeError):
        return datetime.strptime(str(obj), pattern.replace("/", "-"))


to_datetime("2020-01-10 16:39:00")


def a():
    roles = ["ad", "top", "mid", "jungle"] * 2 + ["support"]
    choice_a = random.randint(0, len(roles))
    choice_b = random.randint(0, len(roles))
    return a() if choice_a == choice_b else (choice_a, choice_b)
    # return choice_a == choice_b and a() or choice_a, choice_b
