import os,sys
sys.path.append(os.path.join('C:','Users','remy','Software','Toto'))
import numpy as np
import pandas as pd
from toto.core.totoframe import TotoFrame
import toto
from toto.inputs.txt import TXTfile



filename=r'..\FB3_bott.txt_1243329.0_4829614.0.txt'
tx=TXTfile([filename],colNamesLine=1,skiprows=1,unitNamesLine=0,time_col_name={'Year':'year','Month':'month','Day':'day','Hour':'hour','Min':'Minute','Sec':'Second'})
tx.reads()
tx.read_time()
df=tx._toDataFrame()

#df=tf['test1']['dataframe'].Statistics.common_stats(mag='U',drr='drr')
# df=df[0].Statistics.joint_prob(speed='elev',direction='hvel_U_lev_3.0',period='Tp',args={'method':'Mag vs Dir',\
# 	'folder out':'/tmp/','X Min Res Max(optional)':[2,1,22],'Y Min Res Max(optional)':[0,0.5],'Direction binning':'centred',\
# 	'Direction interval': 45.,'Time blocking':'Monthly','Probablity expressed in':'percent'})
df[0].filename='test'
# df=df[0].Statistics.exc_prob(data='elev',args={'method':'exceedance',\
# 	'folder out':'','Exceedance bins: Min Res Max(optional)':[0,0.01,1],'Duration Min Res Max':[1,1,12],
# 	'Time blocking':'Monthly','Probablity expressed in':'percent'})
df=df[0].Statistics.exc_coinc_prob(data='elev',coincident_nodir='hvel_U_lev_3.0',coincident_with_dir='coincident_with_dir',\
        args={'method':'exceedence',\
        'folder out':'',
        'Exceedance bins: Min Res Max(optional)':[0,.2],
        'Coincidence bins: Min Res Max(optional)':[0,.2],
        'Duration Min Res Max':[6,6,72],
        'Direction binning':{'centered':True},
        'Direction interval': 45.,
        'Time blocking':'Monthly'})
