from threading import Thread
from typing import Callable


def run(fun: Callable, **kwargs):
    """
    run(playback.play, kwargs={"audio_segment": sound})
    run(playback.play(sound))
    """
    Thread(target=fun, kwargs=kwargs).start()
