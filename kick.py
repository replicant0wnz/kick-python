#!/usr/bin/env python3

import math
import os
import struct
import sys

import pyaudio
import mpv

p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

for i in range(0, numdevices):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

stream = p.open(format=pyaudio.paInt16,
                input_device_index=6,
                channels=2,
                rate=44100,
                input=True,
                frames_per_buffer=800)

def rms( data ):
    count = len(data)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, data )
    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0/32768)
        sum_squares += n*n
#    return math.sqrt( sum_squares / count )
    return round(sum_squares)

player = mpv.MPV(ytdl=True)


while True:
    data = stream.read(1024, exception_on_overflow=False)
    x = rms(data)
    if x > 0:
        print(x)
        player.play('bass.wav')
