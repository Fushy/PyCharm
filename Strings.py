from typing import Optional, Match
import re

def replace_texts(text, old_chars, new_chars):
    return re.sub('|'.join(old_chars), lambda match: new_chars[old_chars.index(match.group(0))], text)


def quote(obj, simple=False):
    return "\"" + str(obj) + "\"" if not simple else "'" + str(obj).replace("'", "\'") + "'"


def get_between_text(text, start: str, end: str) -> str:
    i_start = text.find(start)
    i_end = text.find(end, i_start)
    if i_start == -1 or i_end == -1:
        return ""
    find_text = text[i_start + len(start):i_end]
    return find_text


def get_between_text_with_regex(text, start: str, end: str, regex) -> Optional[Match[str]]:
    find_text = get_between_text(text, start, end)
    return regex.search(find_text)


def float_to_spacefloat(n) -> str:
    return "{:,}".format(n).replace(',', ' ')
