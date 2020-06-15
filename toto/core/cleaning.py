
import pandas as pd
import numpy as np




def sort_dataset(df,**args):
    df.sort_index(inplace=True,**args)
    return df

def get_freq(df):
    dt=(df.index[2]-df.index[1]).seconds
    return dt

def filled_gap(df,missing_value=np.NaN):
	    
    df=sort_dataset(df)
    dt=get_freq(df)
    idx = pd.period_range(min(df.index), max(df.index),freq='%is'%dt)
    idx=idx.to_timestamp()
    df=df.reindex(idx, fill_value=missing_value)
    df.index.name='time' 

    return df

def move_var(dfIn,varIn,dfOut,methods='exactly'):
    if methods is 'exactly':
        dfIn[varIn] = dfIn.index.map(dfOut[varIn])
        del  dfOut[varIn]
    else:
        pass

    return dfIn,dfOut

def move_metadata(dfIn,varIn,dfOut):
    dfIn[varIn]=dfOut.pop(varIn)
    return dfIn,dfOut
