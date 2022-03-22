import os,sys
sys.path.append('/home/remy/software/TOTO/Toto')
#sys.path.append('/home/remy/Calypso/Projects/004_Toto/Toto')
import numpy as np
import pandas as pd
from toto.core.totoframe import TotoFrame
import toto
from toto.inputs.txt import TXTfile
from toto.inputs.mat import MATfile
from toto.core.toolbox import dir_interval
from toto.core.wavestats import calc_slp
#Year	Month	Day	H[UTC]	Min	Sec	dpm[deg]	dpm_sea8[deg]	dpm_sw8[deg]	hs[m]	hs_sw8[m]	tp[s]	tp_sea8[s]	tp_sw8[s]	hs_sea8[m]	t02[s]
filename=r'txt_file/cyclones_115.3085_19.8892.txt'
tx=TXTfile([filename],colNamesLine=1,skiprows=1,unitNamesLine=0,time_col_name={'Year':'year','Month':'month','Day':'day','H[UTC]':'hour','Min':'Minute'})
tx.reads()
tx.read_time()
df=tx._toDataFrame()
# filename=r'mat_file/tidal.mat'
# tx=MATfile(filename)
# df=tx._toDataFrame()

    

# df[0].Extreme.do_extreme_adjusted(hs='hs',wspd_optional='hs',\
#         args={'Fitting distributionfor Hs':'Weibull',
#          'Fitting distributionfor Wspd':'Weibull',
#          'Estimation method for Hs':'ml',#{'pkd':False,'pwm':False,'mom':False,'ml':True},
#          'Estimation method for Wspd':'ml',#{'pkd':False,'pwm':False,'mom':False,'ml':True},
#          'Risk level: e.g. 10%, 5%, 1%':[1,5,10],
#          'Max limiting Hs (typically 5 m for barge tow and 8 m for ships':5.0,
#          'Transport speed (m/s)':2.572,
#          'Transport distance (km)':1000.0,
#          'Time blocking':'Monthly',#:True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
#          'Display CDFs':'On',#{'On':True,'Off':False},
#          'folder out':os.getcwd()
#          })

df[0].Extreme.do_extreme(mag='hs',tp='tp',drr='dpm',tm='t02',water_depth='',\
        args={'fitting distribution':'Weibull',
         'method':'ml',#{'pkd':False,'pwm':False,'mom':False,'ml':True},
         'slope fitting distribution':'Gumbel',#:True,'Gumbel':False},
         'slope treshold':0.005,
         'return period':[1,10,25,50,100],
         'estimate Hmax & Cmax RPVs':'On',#:False,'Off':True},
         'threshold type':'value',#:True,'value':False},
         'threshold value':0.5,
         'directional':'Off',#:True,'Off':False},
         'minimum number of peaks over threshold': 5,
         'minimum time interval between peaks (h)':2.0,
         'direction binning':'centered',#:True,'not-centered':False},
         'direction interval': 45.,
         'time blocking':'Annual',#:True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
         'display peaks':'On',#{'On':True,'Off':False},
         'display CDFs':'On',#{'On':True,'Off':False},
         'water depth':-5000.0,
         'folder out':os.getcwd()
         })

# df[0].Extreme.distribution_shape(magnitude='hs',direction_optional='dpm',\
#         args={'Fitting distribution':'Weibull',
#          'Method':'ml',#{'pkd':False,'pwm':False,'mom':False,'ml':True},
#          'threshold type':'percentile',#:True,'value':False},
#          'threshold value':1.0,
#          'Directional':'Off',#:True,'Off':False},
#          'Minimum number of peaks over threshold': 4,
#          'Minimum time interval between peaks (h)':2.0,
#          'Direction binning':'centered',#:True,'not-centered':False},
#          'Direction interval': 45.,
#          'Time blocking':'Monthly',#:True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
#          'Display peaks':'On',#{'On':True,'Off':False},
#          'Display CDFs':'On',#{'On':True,'Off':False},
#          'folder out':os.getcwd()
#          })

# df[0].Extreme.extreme_water_elevation(tide='el_tide',surge='el_res',\
#         args={'Fitting distribution':'Weibull',
#          'Method':'ml',#{'pkd':False,'pwm':False,'mom':False,'ml':True},
#          'Surge':'Both (neg and pos)',#{'Positive only':False,'Negative only':False,'Both (neg and pos)':True},
#          'Return period':[1,10,25,50,100],
#          'threshold type':'percentile',#:True,'value':False},
#          'threshold value':95.0,
#          'Minimum number of peaks over threshold': 3,
#          'Minimum time interval between peaks (h)':24.0,
#          'Time blocking':'Monthly',#:True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
#          'Display peaks':'On',#{'On':True,'Off':False},
#          'Display CDFs':'Off',#{'On':True,'Off':False},
#          'folder out':os.getcwd()
#          })


