#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  main.py
#  
# MIT License
#
# Copyright (c) 2017 Jean Vincent
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import audioExtraction as auEx
import driverMotores as braco
import multiprocessing as mp
import subprocess as sp
import os, sys, time, wave, pyaudio



def main(args):
    if len(args) != 2:
        print("usage: ./main.py <audio file path>")
    else:
        wav_path = args[1]
        path, filename = os.path.split(wav_path)
        filename, extension = os.path.splitext(filename)
        tmp_file_created = False
        pool = mp.Pool(processes=3)
        q = mp.Queue(64)

        try:  # Handle KeyboardInterrupt exception
            
            # Convert compressed formats to a temp wav file
            if extension != ".wav":
                fnull = open(os.devnull, "w")
                pieq_tmp = os.path.expanduser("~") + "/.pieq_tmp/"
                wav_path = pieq_tmp + filename + ".wav"
                
                if not os.path.isfile(wav_path):
                    print("Decompressing...")
                    sp.call(["mkdir", "-p", pieq_tmp])
                    sp.call(["ffmpeg", "-i", args[1], wav_path], stdout=fnull, stderr=sp.STDOUT)
                tmp_file_created = True

            wf = wave.open(wav_path, 'rb')
            nb_channels = wf.getnchannels()
            frame_rate = wf.getframerate()

            # instantiate PyAudio
            pyau = pyaudio.PyAudio()

            # define callback
            def callback(in_data, frame_count, time_info, status):
                data = wf.readframes(frame_count)
                q.put_nowait(data)
                return data, pyaudio.paContinue

            # open stream using callback
            stream = pyau.open(format=pyau.get_format_from_width(wf.getsampwidth()),
                               channels=nb_channels,
                               rate=frame_rate,
                               output=True,
                               stream_callback=callback)

            # start the stream
            pool.apply_async(stream.start_stream)
            # Process the data and display it while the stream is running
            while stream.is_active():
                # This creates a delay so that audio and display are synchronized
                while q.qsize() < 30: 
                    time.sleep(0.05)
                    break
                q_data = q.get(0.1)
                # Calculate and display
                magnitudes = pool.apply(auEx.calculate_magnitudes, (q_data, 1024, nb_channels))
                magnitudes = auEx.get_eq(magnitudes)
                pool.apply_async(bot_dance, magnitudes)

            # stop stream
            stream.stop_stream()
            stream.close()
            wf.close()
           
            # close PyAudio
            pyau.terminate()
            
        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            # Delete temp wav file if necessary
            if tmp_file_created:
                os.remove(wav_path)
            # auVi.clear_display()
            q.close()
            pool.terminate()         
                
    return 0


def bot_dance(*magnitudes):
    def get_dominant(magnitudes):
        list(magnitudes)
        highter = 0
        for frequency in magnitudes:
            if highter < frequency:
                highter = frequency
        return magnitudes.index(highter)
    if get_dominant() == 0:
        angule = (0, 0, 0)
    elif get_dominant() == 1:
        angule = (26, 13, 22)
    elif get_dominant() == 2:
        angule = (52, 25, 45)
    elif get_dominant() == 3:
        angule = (78, 38, 67)
    elif get_dominant() == 4:
        angule = (104, 51, 90)
    elif get_dominant() == 5:
        angule = (130, 64, 112)
    elif get_dominant() == 6:
        angule = (156, 77, 135)
    elif get_dominant() == 7:
        angule = (180, 90, 160)
    print(angule)
    #braco.set_pos(angule)



if __name__ == '__main__':
    sys.exit(main(('.\main.py', '.\\20hz_to_20khz_sweep.wav')))
