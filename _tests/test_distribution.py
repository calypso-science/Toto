import os,sys
import toto
from toto.inputs.txt import TXTfile
import numpy as np
import pandas as pd

filename=os.path.join('txt_file','cyclones_115.3085_19.8892.txt')
tx=TXTfile([filename],colNamesLine=1,skiprows=1,unitNamesLine=0,time_col_name={'Year':'year','Month':'month','Day':'day','H[UTC]':'hour','Min':'Minute'})
tx.reads()
tx.read_time()
df=tx._toDataFrame()[0]
df.filename='test'
df.Extreme.distribution_shape(mag='hs',drr=None,\
        args={'Fitting distribution':'Weibull',
         'method':'ml',#{'pkd':False,'pwm':False,'mom':False,'ml':True},
         'threshold type':'percentile',#:True,'value':False},
         'threshold value':70,
         'directional':False,#:True,'Off':False},
         'minimum number of peaks over threshold': 5,
         'minimum time interval between peaks (h)':2.0,
         'direction binning':'centered',#:True,'not-centered':False},
         'direction interval': 45.,
         'time blocking':'Monthly',#:True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
         'display peaks':True,#{'On':True,'Off':False},
         'display CDFs':False,#{'On':True,'Off':False},
         'folder out':os.getcwd()
         })