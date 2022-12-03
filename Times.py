from datetime import datetime, timedelta
from typing import Callable

import pandas as pd
import pytz

TIMEDELTA_ZERO = timedelta(seconds=0)


def now(utc=False, offset_h=0, offset_m=0, offset_s=0, with_ms=True) -> datetime:
    offset = timedelta(hours=offset_h, minutes=offset_m, seconds=offset_s)
    datetime_now = offset + (datetime.utcnow() if utc else datetime.now())
    return datetime_now if with_ms else datetime_now.replace(microsecond=0)


def to_datetime(obj, pattern: str = "%Y/%m/%d %H:%M:%S") -> datetime:
    if type(obj) is datetime:
        return obj
    try:
        return datetime.fromtimestamp(int(obj))
    except (ValueError, AttributeError, TypeError):
        default_value = pattern == "%Y/%m/%d %H:%M:%S"
        str_obj = str(obj).replace("-", "/") if default_value else str(obj)
        return datetime.strptime(str_obj, pattern)


def to_timestamp(obj, pattern: str = "%Y/%m/%d %H:%M:%S") -> float:
    if type(obj) in (float, int):
        return obj
    try:
        return obj.timestamp()
    except (ValueError, AttributeError, TypeError):
        return to_timestamp(to_datetime(obj, pattern=pattern))


def elapsed_timedelta(date_time: datetime):
    return datetime.now() - date_time


def elapsed_seconds(date_time: datetime):
    return (datetime.now() - date_time).total_seconds()


def elapsed_minutes(date_time: datetime):
    return elapsed_seconds(date_time) / 60


def generate_datetime(start: datetime, end: datetime, freq="T") -> list[str]:
    return sorted(map(str, pd.date_range(start=start, end=end, freq=freq).to_pydatetime().tolist()))


def timeit_trivial(fun: Callable, *args, n=100):
    start = now()
    for _ in range(n):
        fun(*args)
    execution_time = round(elapsed_seconds(start) / n * 1000, 3)
    print(fun.__name__, execution_time, "ms")
    return execution_time


def timeit(fun: Callable, *args) -> float:
    """ Estimate an execution time of a function as milliseconds
    Repeat at least 10 times the function to memoize it into the cache then
    |Repeat at least 1 time the function to refresh it into the cache
    |Estimate the execution time with at least 10 executions, this is regrouped as one execution time by calculating its average
    |Repeat that 5 times
    Calculate the average of estimated executions times
    Return the average of estimated executions times as milliseconds
    """
    repeat_call_min = 10
    sec_elapsed_minimal = 1
    total_repeat = 5
    times_estimate = []
    start = now()
    i = 0
    while elapsed_seconds(start) < sec_elapsed_minimal or i < repeat_call_min:
        # "charging in cache"
        fun() if len(args) == 0 else fun(*args)
        i += 1
        if elapsed_seconds(start) <= sec_elapsed_minimal:
            repeat_call_min += 1
    for _ in range(total_repeat):
        for _ in range(int(repeat_call_min / 10)):
            fun() if len(args) == 0 else fun(*args)
        start = now()
        for _ in range(repeat_call_min):
            fun() if len(args) == 0 else fun(*args)
        times_estimate.append(elapsed_seconds(start) / repeat_call_min)
    execution_time = round(sum(times_estimate) / len(times_estimate) * 1000, 3)
    print(fun.__name__, execution_time, "ms", len(times_estimate) * repeat_call_min, "called")
    return execution_time


def search_tz(city: str) -> pytz:
    """ Cherche une ville dans pytz.all_timezones et retourne sa timezone. """
    return pytz.timezone(list(name for name in pytz.all_timezones if city.capitalize() in name)[0])

# def test(browser, xpath):
#     # test 78.5 ms 25 times
#     return browser.get_element(xpath)
# def test(browser, xpath):
#     # test 136.6 ms 25 times
#     return browser.get_element(xpath).text
# def test(browser, xpath):
#     # test 103.839 ms 25 times
#     return get_element_text(browser.get_element(xpath))
# def test(browser, xpath):
#     # test 102.495 ms 25 times
#     return browser.get_text("", xpath)
