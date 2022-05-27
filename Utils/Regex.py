import re
from datetime import timedelta
from typing import Optional

int_regex = r"([-+]?[0-9]+([eE][-+]?[0-9]+)?)"
float_regex = r"([-+]?[0-9,]*\.?[0-9,]+([eE][-+]?[0-9,]+)?)"
re_time_hms = r"((([0-9]?[0-9]) *h *)?(([0-9]?[0-9]) *m *)?(([0-9]?[0-9]) *s *)?)"
re_time_dot = r"((([0-9]?[0-9]) *: *)?(([0-9]?[0-9]) *: *)([0-9]?[0-9]))"
alphanum_regex = r"([a-zA-Z0-9 +’'|#@_-]+)"
alpha_regex = r"([a-zA-Z ]+)"

re_int = re.compile(int_regex)
re_float = re.compile(float_regex)
re_time_hms = re.compile(re_time_hms)
re_time_dot = re.compile(re_time_dot)
re_alphanum = re.compile(alphanum_regex)
re_alpha = re.compile(alpha_regex)


def search_n_get_float(text: str) -> Optional[float]:
    if text is None:
        return None
    float_find = re_float.search(text)
    if float_find is not None:
        return float(re_float.search(text).group(1).replace(",", ""))


def get_timer(timer: str) -> Optional[list[Optional[float]]]:
    if ":" in timer:
        is_timer = re_time_dot.search(timer)
        _, _, h, _, m, s = is_timer.groups()
    else:
        is_timer = re_time_hms.search(timer)
        _, _, h, _, m, _, s = is_timer.groups()
    if all((x is None for x in [h, m, s])):
        return None
    return list(map(lambda x: 0 if x is None else float(x), (h, m, s)))


def get_timer_as_timedelta(timer: str) -> Optional[timedelta]:
    result = get_timer(timer)
    if result is None:
        return
    h, m, s = result
    return timedelta(hours=h, minutes=m, seconds=s)


if __name__ == '__main__':
    print(re_time_hms.search("01h 02m 03s").groups())
    print(re_time_hms.search("01h 03s").groups())
    print(re_time_hms.search("01m 03s").groups())
    print(re_time_hms.search("01h 03s").groups())
    print(re_time_hms.search("01:02m03s").groups())
    print(get_timer("01h 02m 03s"))
    print(get_timer("01h 03s"))
    print(get_timer("01m 03s"))
    print(get_timer("01h 03s"))
    print(get_timer("3s"))
    print(get_timer("01:02:03"))
    print(get_timer("01 : 02 : 03"))
    print(get_timer("01 : 03"))
    print(get_timer_as_timedelta("01 : 03"))
