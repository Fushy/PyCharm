from threading import Thread
from time import sleep
from typing import Callable

from Files import is_existing, delete

delete("locked")


def run(fun: Callable, wait_a_bit: float = 0.1, **kwargs):
    """
    run(playback.play, kwargs={"audio_segment": sound})
    run(playback.play(sound))
    """
    Thread(target=fun, kwargs=kwargs).start()
    sleep(wait_a_bit)


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
