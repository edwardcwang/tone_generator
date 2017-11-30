#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  tone_generator_demo.py

from tone_generator import ToneGenerator

from math import cos, pi
import time
import sys

def main(args):
    start = time.time()

    freq = 440

    def vary_freq() -> float:
        elapsed_seconds = time.time() - start
        return freq + 100*cos(2*pi*0.1*elapsed_seconds)

    sample_rate2 = 44100 // 2
    sampwidth2 = 2 # 2 bytes = 16 bit

    tone = ToneGenerator()
    tone.set_sampling_info(sample_rate2, sampwidth2)
    tone.samples = tone.create_sine_generator()

    tone.start_audio_thread()
    while True:
        tone.freq = vary_freq()
        time.sleep(0.02)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
