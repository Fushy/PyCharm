import inspect
import os.path
from inspect import FrameInfo

# def current_infos(backtimes=0):
#     print(frameinfo(backtimes))
# print("Current file:", inspect.currentframe().f_code.co_filename)
# print("Current fun:", inspect.stack(1)[0].function)
# print("Current fun:", inspect.currentframe().f_code.co_name)
# print("Current line:", inspect.currentframe().f_lineno)
from typing import Optional


def frameinfo(backtimes=0, debug=False):
    frame = inspect.currentframe()
    for _ in range(backtimes):
        frame = frame.f_back
    pathname = frame.f_code.co_filename
    pathname_complete = pathname
    # fun_name = frame.f_code.co_name
    fun_args = frame.f_locals
    line = frame.f_lineno
    sep = os.path.sep
    if pathname.find(os.path.sep) == -1:
        sep = "/"
    if debug:
        print("Current path:", pathname)
        # print("Current fun:", fun_name)
        print("Current fun args:", fun_args)
        # print("Current line:", line)
        print(os.path.sep, pathname.rfind(sep))
        print(os.path.sep, pathname.rfind("."))
    filename = pathname[pathname.rindex(sep) + 1:pathname.rindex(".")]
    pathname = pathname[:pathname.rindex(sep) + 1]
    if debug:
        print("Current file:", filename)
    # return {"filename": filename, "pathname": pathname, "fun_name": fun_name, "lineno": line, "fun_args": fun_args}
    return {"filename": filename, "pathname": pathname, "fun_args": fun_args, "line": line, "pathname_complete": pathname_complete}


def current_lines(start_depth=2, end_depth: Optional[int] = None):
    i = start_depth
    lst = []
    try:
        while end_depth is None or end_depth < i:
            frame = frameinfo(i)
            lst.append(frame["filename"] + ":" + str(frame["line"]))
            i += 1
    except AttributeError:
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


def current_file():
    return inspect.currentframe().f_code.co_filename
