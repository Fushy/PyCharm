import re

int_regex = r"([-+]?[0-9]+([eE][-+]?[0-9]+)?)"
float_regex = r"([-+]?[0-9,]*\.?[0-9,]+([eE][-+]?[0-9,]+)?)"
timer_regex = r"([0-9][0-9]:[0-9][0-9]:[0-9][0-9])"
timer2_regex = r"(([0-9][0-9])h *?([0-9][0-9])m *?([0-9][0-9])s *)"
alphanum_regex = r"([a-zA-Z0-9 +’'|#@_-]+)"
alpha_regex = r"([a-zA-Z ]+)"

re_int = re.compile(int_regex)
re_float = re.compile(float_regex)
re_timer = re.compile(timer_regex)
re_timer2 = re.compile(timer2_regex)
re_alphanum = re.compile(alphanum_regex)
re_alpha = re.compile(alpha_regex)
