import os
from hashlib import blake2b
from pathlib import Path
from time import sleep

from gtts import gTTS
from pydub import AudioSegment, playback

import Classes
import Threads
from Telegrams import message


def speedup_mp3(file, speed: float = 2):
    sound = AudioSegment.from_file(file)
    new_sound = sound._spawn(sound.raw_data, overrides={"frame_rate": int(sound.frame_rate * speed)})
    new_sound.export(file, format="mp3")


def say(speech: str, filename=None, lang="en", speed: float = 1, blocking=False) -> None:
    # print("say", speech)
    if filename is None:
        encode = blake2b(digest_size=32)
        # encode = blake2b(digest_size=4)
        encode.update(bytes(speech.encode('utf-8')))
        encode.update(bytes(lang.encode('utf-8')))
        encode.update(bytes(str(speed).encode('utf-8')))
        filename = encode.hexdigest()
    pathname = "{}{}Sounds{}mp3{}".format(os.getcwd(), os.path.sep, os.path.sep, os.path.sep)
    if not os.path.exists(pathname):
        Path(pathname).mkdir(parents=True, exist_ok=True)
    filename = pathname + filename + ".mp3"
    if not os.path.exists(filename):
        tts = gTTS(text=speech, lang=lang, slow=False)
        tts.save(filename)
        speedup_mp3(filename, speed=speed)
    try:
        sound = AudioSegment.from_mp3(filename)
        if blocking:
            playback.play(sound)
        else:
            Threads.run(playback.play(sound))
    except FileNotFoundError:
        print(FileNotFoundError)
        sleep(1)
        return say(speech, filename, lang, speed, blocking)


def loop_say(msg, condition: Classes.Condition, seconds=30, blocking=True):
    def fun():
        while not condition.is_done():
            say(msg)
            sleep(seconds)
        print("loop_say end", condition)

    if blocking:
        fun()
    else:
        Threads.run(fun)


def alert(msg: str, level: int = 1, after_sleep: float = 30):
    debug_change = True
    if level == 1:
        message(msg)
        say(msg)
        sleep(after_sleep)
    elif level == 3:
        while debug_change:
            message(msg)
            say(msg)
            sleep(after_sleep)


def notify_win(msg):
    pass
    # toaster = ToastNotifier()
    # toaster.show_toast(msg, threaded=True)


if __name__ == '__main__':
    say("message", blocking=True)
    # say("This is a long message !", blocking=True)
    # say("This is a long message !", speed=1.5, blocking=True)
    # alert("telegram message", after_sleep=0)
