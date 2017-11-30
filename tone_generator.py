#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  tone_generator.py
#  
#  Copyright 2017 Edward Wang <edward.c.wang@compdigitec.com>

from wavebender import *
from wavebender_extra import *
import pyaudio
import threading
import time

from typing import Optional

# Would be nice if Python had this by default.
def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@singleton
class ToneGenerator:
    def __init__(self) -> None:
        # sample_rate: samples/sec
        # sampwidth: sample width in bytes. e.g 2 --> 16 bit
        self.p = pyaudio.PyAudio()

        self.stream = None # type: pyaudio.Stream

        self.thread = None # type: threading.Thread
        self._has_sampling_info = False # type: bool
        self.audio_thread_stop_requested = False # type: bool
        self.audio_thread_stopped = False # type: bool
        self.freq = 440.0
        self.samples = None

    def set_sampling_info(self, sample_rate: int, sampwidth: int) -> None:
        """Set some sampling info required to create a PyAudio stream."""
        self.sample_rate = sample_rate
        self.sampwidth = sampwidth
        self._has_sampling_info = True
        self.stream = self.p.open(
            format = self.p.get_format_from_width(self.sampwidth),
            channels = 1,
            rate = self.sample_rate,
            output = True)

    def create_sine_generator(self, num_samples: Optional[int] = None):
        """Create a default sine generator.
        By default, it creates an infinitely long sine generator whose freq
        can be controlled by .freq."""
        def return_freq():
            return self.freq
        def note():
            return (sine_wave_func(return_freq, amplitude=0.1, framerate=self.sample_rate),)
        channels = (note(),)
        return compute_samples(channels, num_samples)

    def audio_thread(self) -> None:
        """Audio thread worker function."""
        samples = self.samples
        stream = self.stream
        sample_rate = self.sample_rate
        sampwidth = self.sampwidth

        audio_buffer = []

        bufSize = 2048 # Block size
        minimumBuffers = 8 # Minimum number of blocks to keep in buffer

        sleep_time = 0.1 * bufSize / sample_rate # Thread sleep time

        def get_data():
            return get_raw_frame(samples, sample_rate * 60 * 1, framerate=sample_rate, nchannels=1, sampwidth=sampwidth, bufsize=bufSize)

        pyaudio_empty_buf_size = stream.get_write_available()

        def pyaudio_buf_size() -> int:
            return (pyaudio_empty_buf_size - self.stream.get_write_available()) * self.sampwidth

        # Starter audio
        for _ in range(minimumBuffers + 2):
            audio_buffer.append(get_data())

        while not self.audio_thread_stop_requested:
            if pyaudio_buf_size() < bufSize*4:
                for _ in range(5):
                    data = audio_buffer.pop(0)
                    stream.write(data)

            while len(audio_buffer) < minimumBuffers:
                audio_buffer.append(get_data())

            time.sleep(sleep_time)

        self.audio_thread_stopped = True

    def start_audio_thread(self) -> None:
        if self.samples is None:
            print("No samples generator set (set .samples)", file=sys.stderr)
            return
        if not self._has_sampling_info:
            print("No sampling info set (use set_sampling_info())", file=sys.stderr)
            return

        def func() -> None:
            self.audio_thread()
        self.thread = threading.Thread(target=func)
        self.audio_thread_stop_requested = False
        self.audio_thread_stopped = False
        self.thread.start()

    def stop_audio_thread(self) -> None:
        """Send a signal to stop the thread and wait for it to finish."""
        self.audio_thread_stop_requested = True
        while not self.audio_thread_stopped:
            pass

    def close(self) -> None:
        """Close the stream and PyAudio.
        No further functions can be called once this happens."""
        self.stream.close()
        self.p.terminate()
