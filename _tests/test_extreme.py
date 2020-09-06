import os,sys
sys.path.append('/home/remy/Software/Toto')
sys.path.append('/home/remy/Calypso/Projects/004_Toto/Toto')
import numpy as np
import pandas as pd
from toto.core.totoframe import TotoFrame
import toto
from toto.inputs.txt import TXTfile
from toto.core.toolbox import dir_interval
from toto.core.wavestats import calc_slp
#Year	Month	Day	H[UTC]	Min	Sec	dpm[deg]	dpm_sea8[deg]	dpm_sw8[deg]	hs[m]	hs_sw8[m]	tp[s]	tp_sea8[s]	tp_sw8[s]	hs_sea8[m]	t02[s]
filename=r'../P1.txt'
tx=TXTfile([filename],colNamesLine=1,skiprows=1,unitNamesLine=0,time_col_name={'Year':'year','Month':'month','Day':'day','H[UTC]':'hour','Min':'Minute'})
tx.reads()
tx.read_time()
df=tx._toDataFrame()
df[0].Extreme.do_extreme(magnitude='hs[m]',tp_optional='tp[s]',direction_optional='dpm[deg]',tm_optional='t02[s]',water_depth_optional='',\
        args={'Fitting distribution':'Weibull',
         'Method':'ml',#{'pkd':False,'pwm':False,'mom':False,'ml':True},
         'Slope fitting distribution':'Weibull',#:True,'Gumbel':False},
         'Slope treshold':0.005,
         'Return period':[1,10,25,50,100],
         'Estimate Hmax & Cmax RPVs':'On',#:False,'Off':True},
         'threshold type':'value',#:True,'value':False},
         'threshold value':6.0,
         'Directional':'False',#:True,'Off':False},
         'Minimum number of peaks over threshold': 10,
         'Minimum time interval between peaks (h)':24.0,
         'Direction binning':'centered',#:True,'not-centered':False},
         'Direction interval': 45.,
         'Time blocking':'Annual',#:True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
         'Display peaks':'Off',#{'On':True,'Off':False},
         'Display CDFs':'Off',#{'On':True,'Off':False},
         'Water depth':-5000.0,
         'folder out':os.getcwd()
         })


print(df[0].Extreme.eva_stats)


