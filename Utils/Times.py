import datetime
import inspect
from typing import Callable


def now(utc=False) -> datetime:
    return datetime.datetime.utcnow() if utc else datetime.datetime.now()


def elapsed_seconds(date_time: datetime):
    return (datetime.datetime.now() - date_time).total_seconds()


def elapsed_minutes(date_time: datetime):
    return (datetime.datetime.now() - date_time).total_seconds() / 60


def times(fun: Callable, *args):
    repeat = 10
    n = 3
    timer_sec = 0.1
    times_estimate = []
    start = now()
    while elapsed_seconds(start) < timer_sec:
        if len(args) == 0:
            fun(args)
        else:
            fun(*args)
        repeat += 1
    for _ in range(n):
        while elapsed_seconds(start) < timer_sec / 10:
            if len(args) == 0:
                fun(args)
            else:
                fun(*args)
        start = now()
        for i in range(repeat):
            if len(args) == 0:
                fun(args)
            else:
                fun(*args)
        times_estimate.append(elapsed_seconds(start) / repeat)
    print(fun.__name__, round(sum(times_estimate) / len(times_estimate) * 1000, 3), "ms")


def times_n(fun: Callable, n=100, *args):
    start = now()
    for i in range(n):
        fun(*args)
    print(inspect.currentframe().f_code.co_name, fun.__name__, round(elapsed_seconds(start) / n * 1000, 3), "ms")
