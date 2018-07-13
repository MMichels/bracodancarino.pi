import numpy as np
import cv2
import struct


def calculate_magnitudes(data, frame_count, nb_channels):
    """
    Takes audio data in wav format, a frame count and the number of channels
    (mono or stereo) and returns an array of magnitude by frequency
    """
    if nb_channels == 2:    # Strip every other sample point to keep only one channel
        data = np.array(struct.unpack('{n}h'.format(n=nb_channels * frame_count), data))[::2]
    else:
        data = np.array(struct.unpack('{n}h'.format(n=nb_channels * frame_count), data))
        
    windowed_data = np.multiply(data, np.hanning(len(data)))
    
    # Calculate the Fourier Transform coefficients
    dft_array = cv2.dft(np.float32(windowed_data))

    # Return the power in each frequency
    magnitudes = np.add(np.sqrt((dft_array*dft_array).sum(axis=1)), 10)
    log_mag = np.log10(magnitudes)
    return log_mag


def avg_and_rescale(magnitudes):
    # Custom slices following a logarithmic progression
    # that is closer to human hearing
    slice1 = magnitudes[:23]
    slice2 = magnitudes[24:47]
    slice3 = magnitudes[48:79]
    slice4 = magnitudes[80:127]
    slice5 = magnitudes[128:191]
    slice6 = magnitudes[192:255]
    slice7 = magnitudes[256:383]
    slice8 = magnitudes[384:575]

    mags_avged = [sum(slice1 / len(slice1)), sum(slice2 / len(slice2)),
                  sum(slice3 / len(slice3)), sum(slice4 / len(slice4)),
                  sum(slice5 / len(slice5)), sum(slice6 / len(slice6)),
                  sum(slice7 / len(slice7)), sum(slice8 / len(slice8))]

    # Squaring the magnitudes allows for more dynamic variations
    # This is purely visual
    mags_squared = np.square(mags_avged)

    # Slight straightening so that lows and highs magnitudes aren't as disparate
    mags_squared = np.multiply(mags_squared, [0.9, 0.95, 1.0, 1.0, 1.0, 1.0, 1.05, 1.1])

    # Rescale, mag_max determined by trial and error
    mag_max = 30
    mag_scaled = []
    for mag in mags_squared:
        mag_scaled.append((mag / mag_max) * 255)

    return mag_scaled


def get_eq(magnitudes):
    float_magnitudes = avg_and_rescale(magnitudes)
    return float_magnitudes
