import os,sys
sys.path.append('/home/remy/Software/Toto')
sys.path.append('/home/remy/Calypso/Projects/004_Toto/Toto')
import numpy as np
import pandas as pd
from toto.core.totoframe import TotoFrame
import toto
from toto.inputs.txt import TXTfile
from toto.inputs.mat import MATfile
from toto.core.toolbox import dir_interval
from toto.core.wavestats import calc_slp
#Year	Month	Day	H[UTC]	Min	Sec	dpm[deg]	dpm_sea8[deg]	dpm_sw8[deg]	hs[m]	hs_sw8[m]	tp[s]	tp_sea8[s]	tp_sw8[s]	hs_sea8[m]	t02[s]
# filename=r'../P1.txt'
# tx=TXTfile([filename],colNamesLine=1,skiprows=1,unitNamesLine=0,time_col_name={'Year':'year','Month':'month','Day':'day','H[UTC]':'hour','Min':'Minute'})
# tx.reads()
# tx.read_time()
# df=tx._toDataFrame()
filename=r'_tests/mat_file/tidal.mat'
tx=MATfile(filename)
df=tx._toDataFrame()

# df[0].Extreme.do_extreme(magnitude='hs[m]',tp_optional='tp[s]',direction_optional='dpm[deg]',tm_optional='t02[s]',water_depth_optional='',\
#         args={'Fitting distribution':'Weibull',
#          'Method':'ml',#{'pkd':False,'pwm':False,'mom':False,'ml':True},
#          'Slope fitting distribution':'Gumbel',#:True,'Gumbel':False},
#          'Slope treshold':0.005,
#          'Return period':[1,10,25,50,100],
#          'Estimate Hmax & Cmax RPVs':'On',#:False,'Off':True},
#          'threshold type':'value',#:True,'value':False},
#          'threshold value':6.0,
#          'Directional':'On',#:True,'Off':False},
#          'Minimum number of peaks over threshold': 10,
#          'Minimum time interval between peaks (h)':24.0,
#          'Direction binning':'centered',#:True,'not-centered':False},
#          'Direction interval': 45.,
#          'Time blocking':'Monthly',#:True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
#          'Display peaks':'Off',#{'On':True,'Off':False},
#          'Display CDFs':'On',#{'On':True,'Off':False},
#          'Water depth':-5000.0,
#          'folder out':os.getcwd()
#          })
df[0].Extreme.extreme_water_elevation(tide='el_tide',surge='el_res',\
        args={'Fitting distribution':'Weibull',
         'Method':'ml',#{'pkd':False,'pwm':False,'mom':False,'ml':True},
         'Surge':'Both (neg and pos)',#{'Positive only':False,'Negative only':False,'Both (neg and pos)':True},
         'Return period':[1,10,25,50,100],
         'threshold type':'percentile',#:True,'value':False},
         'threshold value':95.0,
         'Minimum number of peaks over threshold': 10,
         'Minimum time interval between peaks (h)':24.0,
         'Time blocking':'Monthly',#:True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
         'Display peaks':'Off',#{'On':True,'Off':False},
         'Display CDFs':'Off',#{'On':True,'Off':False},
         'folder out':os.getcwd()
         })

print(df[0].Extreme.eva_stats)


