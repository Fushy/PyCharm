import glob
import os
from typing import Callable, Optional


def is_existing(path: str) -> bool:
    return os.path.exists(path)


def is_dir(path: str) -> bool:
    return os.path.isdir(path)


def is_file(path: str) -> bool:
    return os.path.isfile(path)


def get_files_from_path(path: str, _filter: Callable[[str], bool] = None, recursive: bool = False) -> list[str]:
    files = glob.glob(path + r"\**\*.*", recursive=recursive)
    if _filter is not None:
        files = list(filter(_filter, files))
    return files


def get_current_files(_filter: Callable[[str], bool] = None, recursive: bool = False) -> list[str]:
    cwd = os.getcwd()
    files = get_files_from_path(cwd, _filter=_filter, recursive=recursive)
    # print("Files in %r: %s" % (cwd, files))
    return files


def get_first_line(file_name: str, encoding="utf-8") -> Optional[str]:
    try:
        with open(file_name, 'r', encoding=encoding) as file:
            return file.readline()
    except FileNotFoundError:
        return None


def get_lines(file_name: str, encoding="utf-8") -> Optional[list[str]]:
    try:
        with open(file_name, 'r', encoding=encoding) as file:
            return file.readlines()
    except FileNotFoundError:
        return None


def count_lines(file_name: str) -> int:
    return sum([1 for _ in open(file_name)])


def abspath(file_name: str) -> Optional[str]:
    if not is_existing(file_name):
        return None
    return os.path.abspath(file_name)


def relpath(file_name: str) -> Optional[str]:
    if not is_existing(file_name):
        return None
    return os.path.relpath(file_name)


def get_current_abspath():
    return os.path.abspath(os.getcwd())


def get_current_path():
    return os.getcwd()


def overwrite(file_name: str, value: str, encoding="utf-8"):
    with open(file_name, 'w', encoding=encoding) as file:
        file.write(str(value))


def append(file_name: str, value: str, encoding="utf-8"):
    with open(file_name, 'a+', encoding=encoding) as file:
        file.write(value)


def delete(file_name: str):
    if is_existing(file_name):
        os.remove(file_name)


def concat_files(dest, *args):
    lines = []
    for file in args:
        file_lines = get_lines(file)
        if file_lines is not None:
            lines.extend(file_lines)
    overwrite(dest, "".join(lines))


def sort_file(file_name, dest, blacklist_lines=None):
    if blacklist_lines is None:
        blacklist_lines = [""]
    blacklist_lines = [line + "\n" for line in blacklist_lines]
    sorted_file = sorted(filter(lambda x: x not in blacklist_lines, get_lines(file_name)))
    overwrite(dest, "".join(sorted_file))


def remove_same_lines(file_name, dest=None):
    if dest is None:
        dest = file_name
    lines = get_lines(file_name)
    new_lines = []
    for i in range(len(lines)):
        if lines[i] not in lines[i + 1:]:
            new_lines.append(lines[i])
    overwrite(dest, "".join(new_lines))


def output(*args, log_file=None, end="\n"):
    concat_args = " ".join([arg for arg in args]) + end
    if log_file is None:
        print(concat_args)
    else:
        append(log_file, concat_args)


def p(*args, log_file=None, end="\n"):
    output(args, log_file, end)


if __name__ == '__main__':
    pre = "B:\\_Documents\\"
    dest1 = pre + "anglais_full.txt"
    dest2 = "anglais.txt"
    # concat_files(dest1, pre + "anglais Fairy tail.txt", pre + "anglais FFVII Remake.txt", pre + "anglais.txt")
    sort_file(dest2, dest=dest2)
    remove_same_lines(dest2)
