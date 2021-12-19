import math
from decimal import Decimal
from random import random
import statistics


def roundup(n):
    decimal = n - int(n)
    return int(n) if decimal < 0.5 else int(n) + 1


def convert(text, x):
    if text == "hours_to_seconds":
        return x * 3600
    elif text == "hours_to_minutes":
        return x * 60
    elif text == "hours_to_days":
        return x / 24


def rng_float_between(a, b):
    return (b - a) * random() + a


def rng_nearly(n, percent):
    return rng_float_between(n * (1 - percent), n * (1 + percent))


def generate_sleep_time(run_time, hit_time):
    """ En secondes """
    pattern = [24, [(0, 0.6689), (5, 0.2), (60, 0.1), (5 * 60, 0.0265), (30 * 60, 0.005)]]
    aim_pause = run_time * 0.1
    hit_per_run = run_time / hit_time
    sleep_per_hit = aim_pause / hit_per_run
    rng = random()
    for sleep_time, odds in pattern[1][::-1]:
        if rng <= odds:
            return rng_nearly(sleep_time * sleep_per_hit / pattern[0], 0.5)
        rng -= odds
    return 0


# if __name__ == '__main__':
#     print(list(filter(lambda x: x != 0, [generate_sleep_time(8 * 60 * 60, 4 * 60) for _ in range(1000000)])))


def float_stepsize(value: float, step_size: float) -> float:
    """
    >>> n = 5.123
    >>> [float_stepsize(n, 1), float_stepsize(n, 0.1), float_stepsize(n, 0.01)]
    [5.0, 5.1, 5.12]
    """
    return round(value, int(round(-math.log(step_size, 10), 0)))


def float_decimal(value, decimal=8) -> str:
    """
    >>> n = 5.123
    >>> [float_decimal(n), float_decimal(n, 0), float_decimal(n, 1), float_decimal(n, 2)]
    ['5.12300000', '5', '5.1', '5.12']
    """
    decimal = "." + str(decimal) + "f"
    return format(float(value), decimal)


def last_decimal_position(number: float) -> tuple[float, int]:
    """ Retourne un doublet contenant le step et la position de la dernière décimal d'un nombre
    >>> last_decimal_position(5.123)
    (0.001, 3)
    >>> print(last_decimal_position(5123)
    (1.0, 0)
    """
    count_decimal = abs(Decimal(str(number)).as_tuple().exponent)
    return 1 / (10 ** count_decimal), count_decimal
