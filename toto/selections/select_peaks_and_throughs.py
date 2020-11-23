""" finds peaks and throughs
    from Nagi Hatoum peaks.m
    copyright 2005"""


import numpy as np

def select_peaks_and_throughs(input_array,args={}):
    y=input_array.to_numpy(copy=True)
    z=input_array.to_numpy(copy=True)
    ds=np.diff(y)
    ds = np.insert(ds, 0, ds[0], axis=0) #pad diff
    fil=np.nonzero((ds[1:]==0))[0]+1 #find zeros
    ds[fil]=ds[fil-1] #replace zeros
    ds=np.sign(ds)
    ds=np.diff(ds)
    t=np.nonzero((ds>0))[0]
    p=np.nonzero((ds<0))[0]

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
