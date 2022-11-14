# import win

# sessions = AudioUtilities.GetAllSessions()
# devices = AudioUtilities.GetSpeakers()
# interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
# volume = cast(interface, POINTER(IAudioEndpointVolume))
# while True:
#     for session in sessions:
#         # if session.Process and session.Process.name() == "Discord.exe":
#         #     print("volume.GetMasterVolumeLevel(): %s" % volume.GetMasterVolumeLevel())
#         print(session.Process)
#     # print(volume.GetMute())
#     # print(volume.GetMasterVolumeLevel())
#     # print(volume.GetVolumeRange())
#     # volume.SetMasterVolumeLevel(-20.0, None)
#     sleep(0.2)

import audioop
import os
import sys
import pyaudio

p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

for i in range(0, numdevices):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
        print("Output Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'),
              p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels'))
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'),
              p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels'))

# === These parameters will be permuted ===========
CHUNKS = [2 ** 9, 2 ** 10, 2 ** 11, 2 ** 12, 2 ** 13, 2 ** 14, 2 ** 15, 2 ** 16]
DEVICES = [4, 7, 9, 10]
RATES = [44100, 48000, 192000]
FORMATS = ['Float32', 'Int32', 'Int24', 'Int16', 'Int8', 'UInt8']
# FORMATS = ['Int16']
CHANNELS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# =================================================

COLUMNS = (('filename', 30),
           ('result', 9),
           ('dev', 5),
           ('rate', 8),
           ('format', 9),
           ('channels', 10),
           ('chunk', 7),
           ('reason', 0))
STATUS_MSG = "Recording... "

pa = pyaudio.PyAudio()


def get_format(format):
    fmt = getattr(pyaudio, 'pa%s' % format)
    return fmt


def record(dev=0,
           filename=None,
           # duration=2,
           rate=44100,
           format='Float32',
           channels=2,
           chunk=1024, ):
    """Record `duration` seconds of audio from the device with index `dev`.
    Store the result in a file named according to recording settings.
    """
    if filename is None:
        filename = "dev{dev}-{rate}-{format}-{channels}ch.raw".format(**locals())
    result = 'FAILURE'
    reason = ''
    outfile = open(filename, 'w')
    print(STATUS_MSG, )
    sys.stdout.flush()
    try:
        stream = pa.open(input_device_index=dev,
                         rate=rate,
                         format=get_format(format),
                         channels=channels,
                         frames_per_buffer=chunk,
                         input=True,
                         )
        try:
            # for i in range(0, rate / (chunk) * duration):
            #     a = stream.read(chunk)
            #     outfile.write(a)
            data = stream.read(chunk, True)
            # data = stream.read(chunk, False)
            audioop.rms(data, 2)
            audioop.max(data, 2)
            result = 'SUCCESS'
        # Catch exceptions when trying to read from stream
        except Exception as e:
            reason = "open '%s'" % e
    # Catch exceptions when trying to even open the stream
    except Exception as e:
        reason = "read '%s'" % e
    outfile.close()
    # Don't leave files behind for unsuccessful attempts
    if result == 'FAILURE':
        os.remove(filename)
        filename = ''
    info = {}
    for col_name, width in COLUMNS:
        info[col_name] = str(locals()[col_name]).ljust(width)
    msg = "{filename}{result}{dev}{rate}{format}{channels}{chunk}{reason}"
    print(msg.format(**info))


def find_correct_record():
    # https://stackoverflow.com/questions/19692003/capture-192-khz-audio-using-python-3?noredirect=1&lq=1
    # Build the header line
    header = 'STATUS'.ljust(len(STATUS_MSG) + 1)
    for col_name, width in COLUMNS:
        header += col_name.upper().ljust(width)
    print(header)
    print("=" * len(header))
    # Record samples for all permutations of our parameter lists
    for chuck in CHUNKS:
        for dev in DEVICES:
            for rate in RATES:
                for _format in FORMATS:
                    for channels in CHANNELS:
                        record(dev=dev,
                               # duration=2,
                               rate=rate,
                               format=_format,
                               channels=channels,
                               chunk=chuck)


if __name__ == '__main__':
    find_correct_record()
