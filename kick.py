#!/usr/bin/env python3

import math
import os
import struct
import sys

import pyaudio
import mpv
import yaml


class KickDrum:
    """
    Simple non-velcotiy drum module specifically for kick drums but could be
    used for any drum pad

    """

    def __init__(self, config_file="config.yaml"):
        """
        Keywords:
            config_file (str): Full path to config
        """

        self.config_file = config_file

    def _read_config(self):
        """
        Reads the yaml config file

        Returns:
            config (dict)
        """

        try:
            f = open(self.config_file)
        except FileNotFoundError as e:
            print(e)

        config_yaml = yaml.load(f.read(), Loader=yaml.FullLoader)

        return config_yaml

    def _open_device(self):
        """
        Creates a pyaudio interface object
        """
        interface = pyaudio.PyAudio()

        return interface

    def _open_stream(
        self, interface=None, input_device_index=None, channels=None, rate=None
    ):
        """
        Open a stream on the sepcific device
        """
        stream = interface.open(
            format=pyaudio.paInt16,
            input_device_index=input_device_index,
            channels=channels,
            rate=rate,
            input=True,
            frames_per_buffer=800,
        )

        return stream

    def _rms(self, data):
        """
        Convert stream data into numberical format
        """
        count = len(data) / 2
        format = "%dh" % (count)
        shorts = struct.unpack(format, data)
        sum_squares = 0.0

        for sample in shorts:
            n = sample * (1.0 / 32768)
            sum_squares += n * n

        return round(sum_squares)

    def _player(self):
        """
        Use mpv to output sound
        """
        player = mpv.MPV()

        return player

    def list_devices(self, interface=None):
        """
        List available input devices
        """
        info = interface.get_host_api_info_by_index(0)
        numdevices = info.get("deviceCount")

        for i in range(0, numdevices):
            if (
                interface.get_device_info_by_host_api_device_index(0, i).get(
                    "maxInputChannels"
                )
            ) > 0:
                print(
                    "Input Device id ",
                    i,
                    " - ",
                    interface.get_device_info_by_host_api_device_index(0, i).get(
                        "name"
                    ),
                )

    def start_controller(self, stream=None):
        """
        Start the loop and listen for events
        """

        config = self._read_config()["config"]
        interface = self._open_device()
        stream = self._open_stream(
            interface=interface,
            input_device_index=config["device_id"],
            channels=config["channels"],
            rate=config["rate"],
        )
        player = self._player()

        while True:
            data = stream.read(1024, exception_on_overflow=False)
            x = self._rms(data)
            if x > config["threshold"]:
                print(x)
                player.play(config["sample"])
