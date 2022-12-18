import sys
import threading
import traceback
from threading import Thread
from time import sleep
from typing import Callable

import Alert
from Files import is_existing, delete, run_file
from Introspection import frameinfo

delete("locked")


def run(fun: Callable, wait_a_bit: float = 0.0, alert_if_error=True, **kwargs) -> threading:
    """
    run(playback.play, kwargs={"audio_segment": sound})
    run(playback.play(sound))
    """

    def aux():
        # noinspection PyBroadException
        try:
            fun()
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)
            print(fun.__name__, file=sys.stderr)
            Alert.alert(str(fun.__name__), level=3)

    thread = Thread(target=aux if alert_if_error else fun, kwargs=kwargs)
    thread.start()
    sleep(wait_a_bit)
    return thread


def loop_run(fun: Callable, sleep_after_execution: float = 0.1, pre_sleep=0, **kwargs):
    def loop():
        sleep(pre_sleep)
        while True:
            if not is_existing(locker_name):
                # print("execution started")
                run(fun, 0.1, **kwargs)
            while is_existing(locker_name):
                sleep(0.001)
            # print("execution ended")
            sleep(sleep_after_execution)

    locker_name = "locked_" + fun.__name__
    delete(locker_name)
    run(loop)


def exit_n_rerun():
    old_frame = None
    i = 0
    while True:
        frame = frameinfo(i)
        if frame is None:
            break
        #     i += 1
        #     continue
        if frame["filename"] == "_pydev_execfile":
            break
        old_frame = frame
        i += 1
    file = old_frame["pathname_complete"]
    # file = r"B:\_Documents\Pycharm\Util\test.ahk"
    run_file(file)
    exit()


def rerun_if_stop(fun):
    while True:
        thread = run(fun)
        thread.join()
