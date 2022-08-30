import math
from datetime import timedelta
from decimal import Decimal
from random import random, randint


def roundup(n):
    decimal_part = n - int(n)
    return int(n) if decimal_part == 0 else int(n) + 1


def convert(text, x):
    if text == "hours_to_seconds":
        return x * 3600
    elif text == "hours_to_minutes":
        return x * 60
    elif text == "hours_to_days":
        return x / 24
    # todo


def rng_int_between(minimal: int, maximal: int) -> int:
    return randint(minimal, maximal)


def rng_float_between(a: float, b: float) -> float:
    return (b - a) * random() + a


def rng_nearly(n, percent, floor=False) -> float:
    return rng_float_between(n * (1 - percent) if not floor else 0,
                             n * (1 + percent) if not floor else n * percent)


def rng_nearly_timedelta(n, percent, floor=False) -> timedelta:
    return timedelta(seconds=rng_nearly(n, percent, floor))


def generate_sleep_time(hit_cooldown=120):
    """ En secondes
    >>> sample = [timedelta(seconds=generate_sleep_time(120)) for _ in range(200000)]
    >>> print(sum(sample, timedelta(0)) / len(sample))
    """
    pattern = [24, [(0, 0.6689), (5, 0.2), (60, 0.1), (5 * 60, 0.05), (30 * 60, 0.005)]]
    aim_pause_per_hit = hit_cooldown * 0.1
    rng = random()
    for sleep_time, odds in pattern[1][::-1]:
        if rng <= odds:
            return rng_nearly(sleep_time * aim_pause_per_hit / pattern[0], 0.25)
        rng -= odds
    return 0


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


# if __name__ == '__main__':
#     a = 10
#     b = 0.2
#     print([rng_nearly(a, b, floor=True) for _ in range(1000)])
#     print(max([rng_nearly(a, b, floor=True) for _ in range(1000)]))
#     print(min([rng_nearly(a, b, floor=True) for _ in range(1000)]))
#     sample = [timedelta(seconds=generate_sleep_time(120)) for _ in range(200000)]
#     print(min(sample))
#     print(max(sample))
#     print(sum(sample, timedelta(0)) / len(sample))
