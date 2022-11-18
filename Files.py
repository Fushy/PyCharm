import os
import shutil
from typing import Callable, Optional

import Introspection


def is_existing(path: str) -> bool:
    """ Due to concurrency, after an is_existing call, it may be possible that the file doesn't exist,
    in this case, use a try-catch exception when the file is used """
    return os.path.exists(path)


def is_dir(path: str) -> bool:
    return os.path.isdir(path)


def is_file(path: str) -> bool:
    return os.path.isfile(path)


def get_files_from_path(*paths: str, _filter: Callable[[str], bool] = None, recursive: bool = False) -> list[str]:
    import glob
    files = []
    for path in paths:
        files += glob.glob(path + r"\*.*")
        if recursive:
            files += glob.glob(path + r"\**\*.*", recursive=recursive)
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


def get_first_part(file_name):
    return file_name[:file_name.rfind(os.sep) + 1]


def get_last_part(file_name):
    return file_name[file_name.rfind(os.sep) + 1:file_name.rfind(".")]


def get_ext(file_name):
    return file_name[file_name.rfind(".") + 1:]


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


def get_project_path():
    """current file dir - 1 """
    return Introspection.frameinfo(2)["pathname"]


def overwrite(file_name: str, value: str, encoding="utf-8", mode="w"):
    if "b" in mode:
        with open(file_name, mode) as file:
            file.write(str(value))
    else:
        with open(file_name, mode, encoding=encoding) as file:
            file.write(str(value))


def append(file_name: str, value: str, encoding="utf-8", mode="a+"):
    if "b" in mode:
        with open(file_name, mode) as file:
            file.write(value)
    else:
        with open(file_name, mode, encoding=encoding) as file:
            file.write(value)


def delete(file_name: str):
    try:
        os.remove(file_name)
    except FileNotFoundError:
        pass


def move_to(file_name: str, dest: str):
    shutil.move(file_name, dest)


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


def is_ascii(text):
    return all(ord(char) < 128 for char in text)


def run_file(file):
    os.system('"' + file + '"')


def run_cmd(cmd):
    os.system('"' + cmd + '"')


if __name__ == '__main__':
    # pre = "B:\\_Documents\\"
    # dest1 = pre + "anglais_full.txt"
    # concat_files(dest1, pre + "anglais Fairy tail.txt", pre + "anglais FFVII Remake.txt", pre + "anglais.txt")
    dest = "anglais.txt"
    sort_file(dest, dest=dest)
    remove_same_lines(dest)
