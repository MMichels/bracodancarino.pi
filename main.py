import audioExtraction as auEx
# import driverMotores as braco
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
                #pool.apply_async(print, magnitudes)
                bot_dance(magnitudes)

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


def bot_dance(mag):
    def get_dominant(magnit):
        list(magnit)
        highter = 0
        for frequency in magnit:
            if highter < frequency:
                highter = frequency
        return magnit.index(highter)
    if get_dominant(mag) == 0:
        angule = (0, 0, 0)
    elif get_dominant(mag) == 1:
        angule = (26, 13, 22)
    elif get_dominant(mag) == 2:
        angule = (52, 25, 45)
    elif get_dominant(mag) == 3:
        angule = (78, 38, 67)
    elif get_dominant(mag) == 4:
        angule = (104, 51, 90)
    elif get_dominant(mag) == 5:
        angule = (130, 64, 112)
    elif get_dominant(mag) == 6:
        angule = (156, 77, 135)
    elif get_dominant(mag) == 7:
        angule = (180, 90, 160)
    print(angule)
    #braco.set_pos(angule)



if __name__ == '__main__':
    sys.exit(main(('.\main.py', '.\\20hz_to_20khz_sweep.wav')))
