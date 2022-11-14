import string
from datetime import timedelta
from random import randint, random, choice


def rng_int_between(minimal: int, maximal: int) -> int:
    return randint(minimal, maximal)


def rng_float_between(a: float, b: float) -> float:
    return (b - a) * random() + a


def rng_nearly(n, percent, floor=False) -> float:
    return rng_float_between(n * (1 - percent) if not floor else 0,
                             n * (1 + percent) if not floor else n * percent)


def rng_nearly_timedelta(n, percent, floor=False) -> timedelta:
    return timedelta(seconds=rng_nearly(n, percent, floor))

def rng_letter():
    return choice(string.ascii_letters)

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