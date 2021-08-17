"""Extract all the peaks and throughs from a timeseries.

    Parameters
    ~~~~~~~~~~

    input_array : (Panda Obj)
        The Panda dataframe.

    Examples:
    ~~~~~~~~~

    >>> df['selected']=select_peaks_and_throughs.select_peaks_and_throughs(
    df['signal'].copy())
    >>> 
"""

from ..core.toolbox import peaks
import numpy as np

def select_peaks_and_throughs(input_array,args={}):
    y=input_array.to_numpy(copy=True)
    z=input_array.to_numpy(copy=True)
    p,t=peaks(y)
    
    z[:]=np.nan
    z[t]=y[t]
    z[p]=y[p]

    input_array.values[:]=z
    return input_array



if __name__ == '__main__':
    import pandas as pd
    T = 100
    x = np.arange(0,T)
    y=  np.sin(4*np.pi*x/T)+np.cos(8*np.pi*x/T)

    df = pd.DataFrame(y, columns=list('e'))
    select_peaks_and_throughs(df)
