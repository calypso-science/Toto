import numpy as np
from scipy.fftpack import fft,rfft, irfft, fftfreq


def bandpass_filter(input_array,args={'lower cut-off':float(),'upper cut-off':float()}):
    output_array=input_array.copy()
    low=args['lower cut-off']
    high=args['upper cut-off']
    dt=(input_array.index[1]-input_array.index[0]).total_seconds()
    input_array.interpolate(inplace=True)
    signal=input_array.values




    W = fftfreq(signal.size, d=dt)
    f_signal = rfft(signal)

    # If our original signal time was in seconds, this is now in Hz    
    cut_f_signal = f_signal.copy()
    if (low == None) or (high == None):

        if low is None:
            cut_f_signal[(W>1/high)] = 0
        else:
            cut_f_signal[(W<1/low)] = 0
    else:
        cut_f_signal[(W>1/high) | (W<1/low)] = 0


    cut_signal = irfft(cut_f_signal)

    output_array.values[:]=cut_signal

    return output_array