import copy
import os
import string
from hashlib import blake2b
from math import log
from pathlib import Path
from random import random
from time import sleep

from faker import Faker
from gtts import gTTS
from pydub import AudioSegment, playback

import Classes
import Threads
from Files import is_existing, delete
from Telegrams import message
from rng import rng_letter


def db_to_float(db, using_amplitude=True):
    """
    Converts the input db to a float, which represents the equivalent
    ratio in power.
    """
    db = float(db)
    if using_amplitude:
        return 10 ** (db / 20)
    else:  # using power
        return 10 ** (db / 10)


def ratio_to_db(ratio, val2=None, using_amplitude=True):
    """
    Converts the input float to db, which represents the equivalent
    to the ratio in power represented by the multiplier passed in.
    """
    ratio = float(ratio)
    # accept 2 values and use the ratio of val1 to val2
    if val2 is not None:
        ratio = ratio / val2
    # special case for multiply-by-zero (convert to silence)
    if ratio == 0:
        return -float('inf')
    if using_amplitude:
        return 20 * log(ratio, 10)
    else:  # using power
        return 10 * log(ratio, 10)


def little_sound(duration_seconds=0.4, volume=0.1):
    sound = say("Hello world !", speed=2, just_create_file=True)
    sound = cut_sound(sound, cut_percent=40)
    sound = change_volume(sound, volume)
    sound = change_duration(sound, duration_seconds)
    play_sound(sound)


def err_sound():
    sound = say("err", just_create_file=True)
    play_sound(cut_sound(sound, cut_percent=49) * 50, blocking=True)


def cut_sound(sound: str | AudioSegment, cut_percent) -> AudioSegment:
    if type(sound) is str:
        sound = AudioSegment.from_mp3(sound)
    if cut_percent > 0:
        milliseconds = int(len(sound) * cut_percent / 100)
        return sound[milliseconds:-milliseconds]
    return sound


def concat_sound(*sounds, cut_percent=5):
    return sum([cut_sound(sound, cut_percent) for sound in sounds])


def change_duration(sound: str | AudioSegment, duration_seconds: float = 1) -> AudioSegment:
    if type(sound) is str:
        sound = AudioSegment.from_mp3(sound)
    length_max = int(duration_seconds * 1000)
    if len(sound) >= length_max:
        return sound[:length_max]
    length: float = duration_seconds / sound.duration_seconds
    # cursor = length % 1
    # new_sound = []
    # i = 0
    # for i in range(len(sound)):
    #     segment = sound[i]
    #     while cursor >= 1:
    #         new_sound.append(segment)
    #         cursor -= 1
    #     else:
    #         cursor += length
    # while cursor >= 1:
    #     new_sound.append(sound[i])
    #     cursor -= 1
    # return sum(new_sound)
    return sound * int(length)


def speedup(sound: str | AudioSegment, speed_ratio: float = 2) -> AudioSegment:
    if type(sound) is str:
        sound = AudioSegment.from_mp3(sound)
    # noinspection PyProtectedMember
    new_sound = sound._spawn(sound.raw_data, overrides={"frame_rate": int(sound.frame_rate * speed_ratio)})
    save(new_sound, "temp.mp3")
    new_sound = read("temp.mp3")
    delete("temp.mp3")
    return new_sound


def change_volume(sound: str | AudioSegment, volume_ratio: float = 0):
    if type(sound) is str:
        sound = AudioSegment.from_mp3(sound)
    new_sound = sound + ratio_to_db(volume_ratio)
    return new_sound


def play_sound(sound: str | AudioSegment, blocking=False) -> AudioSegment:
    try:
        if type(sound) is str:
            sound = AudioSegment.from_mp3(sound)
        if blocking:
            playback.play(sound)
        else:
            Threads.run(playback.play(sound))
        return sound
    except FileNotFoundError:
        print(FileNotFoundError)
        sleep(1)
        return play_sound(sound, blocking)


def save(sound: AudioSegment, dest: str):
    sound.export(dest, format="mp3")


def read(filename: str):
    return AudioSegment.from_mp3(filename)


def say(speech: str, filename=None, lang="en", speed: float = 1, blocking=False,
        volume_ratio: float = 1, just_create_file=False, save_sound=True) -> AudioSegment:
    # print("say", speech)
    if filename is None:
        encode = blake2b(digest_size=32)
        # encode = blake2b(digest_size=4)
        encode.update(bytes(speech.encode('utf-8')))
        encode.update(bytes(lang.encode('utf-8')))
        encode.update(bytes(str(speed).encode('utf-8')))
        encode.update(bytes(str(volume_ratio).encode('utf-8')))
        filename = encode.hexdigest()
    pathname = "{}{}Sounds{}mp3{}".format(os.getcwd(), os.path.sep, os.path.sep, os.path.sep)
    if not os.path.exists(pathname):
        Path(pathname).mkdir(parents=True, exist_ok=True)
    filename = pathname + filename + ".mp3"
    if not is_existing(filename):
        tts = gTTS(text=speech, lang=lang, slow=False)
        tts.save(filename)
        sound = read(filename)
        sound = speedup(sound, speed_ratio=speed)
        sound = change_volume(sound, volume_ratio=volume_ratio)
        if save_sound:
            save(sound, filename)
    else:
        sound = AudioSegment.from_mp3(filename)
    if not just_create_file:
        return play_sound(sound, blocking)
    return sound


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
    # say("message", blocking=True)
    # say("This is a long message !", blocking=True)
    # say("This is a long message !", speed_ratio=1.5, blocking=True)
    alert("telegram message", after_sleep=0)
