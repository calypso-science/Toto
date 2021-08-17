""" Find Peaks using the scipy function and replace them with NaN.

    Parameters
    ~~~~~~~~~~
    input_array : Panda Obj
        The Panda dataframe.
    height : number or ndarray or sequence, optional
        Required height of peaks. Either a number, ``None``, an array matching
        `x` or a 2-element sequence of the former. The first element is
        always interpreted as the  minimal and the second, if supplied, as the
        maximal required height.
    threshold : number or ndarray or sequence, optional
        Required threshold of peaks, the vertical distance to its neighboring
        samples. Either a number, ``None``, an array matching `x` or a
        2-element sequence of the former. The first element is always
        interpreted as the  minimal and the second, if supplied, as the maximal
        required threshold.
    distance : number, optional
        Required minimal horizontal distance (>= 1) in samples between
        neighbouring peaks. Smaller peaks are removed first until the condition
        is fulfilled for all remaining peaks.
    prominence : number or ndarray or sequence, optional
        Required prominence of peaks. Either a number, ``None``, an array
        matching `x` or a 2-element sequence of the former. The first
        element is always interpreted as the  minimal and the second, if
        supplied, as the maximal required prominence.
    width : number or ndarray or sequence, optional
        Required width of peaks in samples. Either a number, ``None``, an array
        matching `x` or a 2-element sequence of the former. The first
        element is always interpreted as the  minimal and the second, if
        supplied, as the maximal required width.
    wlen : int, optional
        Used for calculation of the peaks prominences, thus it is only used if
        one of the arguments `prominence` or `width` is given. See argument
        `wlen` in `peak_prominences` for a full description of its effects.
    rel_height : float, optional
        Used for calculation of the peaks width, thus it is only used if `width`
        is given. See argument  `rel_height` in `peak_widths` for a full
        description of its effects.
    plateau_size : number or ndarray or sequence, optional
        Required size of the flat top of peaks in samples. Either a number,
        ``None``, an array matching `x` or a 2-element sequence of the former.
        The first element is always interpreted as the minimal and the second,
        if supplied as the maximal required plateau size.


    Notes
    ~~~~~
    see https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html
"""

import numpy as np
from scipy.signal import find_peaks

def spike_removal(input_array,args={'height':float(),
                                    'threshold':float(),
                                    'distance':float(),
                                    'prominence':float(),
                                    'width':float(),
                                    'wlen':float(),
                                    'rel_height':float(),
                                    'plateau_size':int()
                                    }):

    if 'LonLat' in args:
        args.pop('LonLat')

    y=input_array.to_numpy(copy=True)
    keys=list(args.keys())
    for key in keys:
        if args[key]==0:
            args.pop(key)


    ind = find_peaks(y,**args)[0]
    
    y[ind]=np.nan
    input_array.values[:]=y

   
    return input_array