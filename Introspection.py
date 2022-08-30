import inspect
import os.path
from inspect import FrameInfo
from typing import Optional


def frameinfo(backtimes=0, debug=False):
    frame = inspect.currentframe()
    try:
        for _ in range(backtimes):
            frame = frame.f_back
        pathname = frame.f_code.co_filename
    except AttributeError:
        # print("backtimes is too high")
        return None
    pathname_complete = pathname
    # fun_name = frame.f_code.co_name
    local_args = frame.f_locals
    line = frame.f_lineno
    sep = os.path.sep
    if pathname.find(os.path.sep) == -1:
        sep = "/"
    if debug:
        print("Current path:", pathname)
        # print("Current fun:", fun_name)
        print("Current fun args:", local_args)
        # print("Current line:", line)
        print(os.path.sep, pathname.rfind(sep))
        print(os.path.sep, pathname.rfind("."))
    try:
        filename = pathname[pathname.rindex(sep) + 1:pathname.rindex(".")]
        pathname = pathname[:pathname.rindex(sep) + 1]
    except ValueError:
        filename = "debuging"
        pathname = "debuging"
    if debug:
        print("Current file:", filename)
    # return {"filename": filename, "pathname": pathname, "fun_name": fun_name, "lineno": line, "local_args": local_args}
    return {"filename": filename,
            "line": line,
            "pathname": pathname,
            "pathname_complete": pathname_complete,
            "local_args": local_args}


def current_infos(backtimes=0):
    print(frameinfo(backtimes))


def current_file():
    return inspect.currentframe().f_code.co_filename


def current_lines(start_depth=2, end_depth: Optional[int] = None):
    i = start_depth
    lst = []
    try:
        while end_depth is None or end_depth < i:
            frame = frameinfo(i)
            if frame is None:
                break
            lst.append(frame["filename"] + ":" + str(frame["line"]))
            i += 1
    except AttributeError:
        return lst
    return lst


def frameinfo_stack(stack=0, debug=False):
    """ ne fonctionne pas dans les threads"""
    frame: FrameInfo = inspect.stack()[stack]
    pathname = frame.filename
    sep = os.path.sep
    if pathname.find(os.path.sep) == -1:
        sep = "/"
    if debug:
        print("Current path:", pathname)
        print("Current fun:", frame.function)
        print("Current line:", frame.lineno)
        print(os.path.sep, pathname.rfind(sep))
        print(os.path.sep, pathname.rfind("."))
    filename = pathname[pathname.rindex(sep) + 1:pathname.rindex(".")]
    if debug:
        print("Current file:", filename)
    return {"filename": filename, "pathname": pathname, "function": frame.function, "lineno": frame.lineno}


if __name__ == '__main__':
    print(current_file())
    print(current_lines())
    print(current_infos())
    print(frameinfo_stack())
