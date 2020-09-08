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
    ind = find_peaks(y,**args)[0]
    
    y[ind]=np.nan
    input_array.values[:]=y

   
    return input_array