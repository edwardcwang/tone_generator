#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  wavebender_extra.py

from wavebender import *

def return_440():
    return 440.0

def sine_wave_func(frequency_func=return_440, framerate=44100, amplitude=0.5,
        skip_frame=0):
    '''
    Generate a sine wave at a variable frequency of infinite length.
    '''
    if amplitude > 1.0: amplitude = 1.0
    if amplitude < 0.0: amplitude = 0.0

    # Keep track of previous phi to prevent phase discontinuities when changing
    # frequency.
    phi = 0

    for i in count(skip_frame):
        phi += 2.0 * math.pi * float(frequency_func()) * (1 / float(framerate))
        sine = math.sin(phi)
        yield float(amplitude) * sine

def get_raw_frame(samples, nframes=None, nchannels=2, sampwidth=2, framerate=44100, bufsize=2048):
    max_amplitude = float(int((2 ** (sampwidth * 8)) / 2) - 1)

    # split the samples into chunks (to reduce memory consumption and improve performance)
    chunk = next(grouper(bufsize, samples)) # grouper returns an iterator
    frames = b''.join(b''.join(struct.pack('h', int(max_amplitude * sample)) for sample in channels) for channels in chunk if channels is not None)

    return frames
