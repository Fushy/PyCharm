import os
from hashlib import blake2b
from time import sleep

from gtts import gTTS
from pydub import AudioSegment, playback
from pathlib import Path

# How to install ffmpeg to pydub
# http://blog.gregzaal.com/how-to-install-ffmpeg-on-windows/
import Threads
import Classes
from Telegrams import telegram_msg


def speedup_mp3(file, speed: float = 2):
    sound = AudioSegment.from_file(file)
    new_sound = sound._spawn(sound.raw_data, overrides={"aframe_rate": int(sound.frame_rate * speed)})
    new_sound.export(file, format="mp3")


def say(speech: str, filename=None, lang="en", speed: float = 1, blocking=False) -> None:
    print("say", speech)
    if filename is None:
        encode = blake2b(digest_size=32)
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
    sound = AudioSegment.from_mp3(filename)
    if blocking:
        playback.play(sound)
    else:
        Threads.run(playback.play(sound))


def loop_say(msg, condition: Classes.Condition, seconds=30, blocking=True):
    def fun():
        while not condition.is_done():
            say(msg)
            sleep(seconds)
        print("loop_say end", condition)
    fun() if blocking else Threads.run(fun)


def alert(msg, level):
    if level == 3:
        for _ in range(2):
            say(msg)
            telegram_msg("Hello !")
            sleep(3)


def notify_win(msg):
    pass
    # toaster = ToastNotifier()
    # toaster.show_toast(msg, threaded=True)
