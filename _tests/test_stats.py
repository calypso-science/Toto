import os,sys
sys.path.append('/home/remy/Software/Toto')
sys.path.append('/home/remy/Calypso/Projects/004_Toto/Toto')
import numpy as np
import pandas as pd
from toto.core.totoframe import TotoFrame
import toto
from toto.inputs.txt import TXTfile
from toto.inputs.mat import MATfile
from toto.inputs.TRYAXIS import TRYAXISfile
import totoView
from toto.plugins.wave._do_ssh_to_wave import zero_crossing

# filename=r'_tests/txt_file/GSB.txt'
# tx=TXTfile([filename],colNamesLine=1,skiprows=1,unitNamesLine=0,time_col_name={'year':'year','month':'month','day':'day','hour':'hour','min':'Minute'})
# tx.reads()
# tx.read_time()
# df=tx._toDataFrame()
# df[0].filename='sss'
filename=r'../ssh2.mat'
tx=MATfile(filename)
# tx=TXTfile([filename],colNamesLine=1,skiprows=1,unitNamesLine=0,time_col_name={'year':'year','month':'month','day':'day','hour':'hour','min':'Minute'})
# tx.reads()
# tx.read_time()
df=tx._toDataFrame()
df[0].filename='sss'



#df=tf['test1']['dataframe'].Statistics.common_stats(mag='U',drr='drr')
# # df=df[0].Statistics.joint_prob(speed='elev',direction='hvel_U_lev_3.0',period='Tp',args={'method':'Mag vs Dir',\
# # 	'folder out':'/tmp/','X Min Res Max(optional)':[2,1,22],'Y Min Res Max(optional)':[0,0.5],'Direction binning':'centred',\
# # 	'Direction interval': 45.,'Time blocking':'Monthly','Probablity expressed in':'percent'})
# df[0].filename='test'
# df=df[0].Statistics.exc_prob(data='elev',args={'method':'exceedance persistence',\
# 	'folder out':'','Exceedance bins: Min Res Max(optional)':[0,0.1],'Duration Min Res Max':[1,1,12],
# 	'Time blocking':'Monthly','Probablity expressed in':'percent'})
# df=df[0].Statistics.exc_coinc_prob(data='elev',coincident_nodir='hvel_U_lev_3.0',coincident_with_dir='coincident_with_dir',\
#         args={'method':'exceedence',\
#         'folder out':'',
#         'Exceedance bins: Min Res Max(optional)':[0,.2],
#         'Coincidence bins: Min Res Max(optional)':[0,.2],
#         'Direction binning':{'centered':True},
#         'Direction interval': 45.,
#         'Time blocking':'Monthly'})

# df[0]['elev'].short_name='E'
# df=df[0].TideAnalysis.tidal_stat(mag='Ve',\
#         args={'Minimum SNR':2,\
#         'Latitude':-36.0,
#         'folder out':'/tmp/',
#         })


# df=df[0].Statistics.workability(data1='Spd',data2='Dir',data3_optional='data3_optional',data4_optional='data4_optional',\
#         args={'method':'persistence exceedence',\
#                'folder out':'/tmp/',
#                'Threshold for each dataset:':[0.5,300], 
#                'Duration Min Res Max':[6,6,72], 
#                'Time blocking':'Monthly'})


# df=df[0].StatPlots.plot_roses(mag='Spd',drr='Dir',\
#         args={'Title':'Current speed',\
#         'units':'m/s',\
#         'Speed bins (optional)':[],
#         '% quadran (optional)':[],
#         'Time blocking':'Annual',
#         'folder out':'/tmp/',
#         })
# df=df[0].StatPlots.Percentage_of_occurence(mag='Spd',drr='Dir',\
#                args={ 'Magnitude interval (optional)':[],
#                 'X label':'Wind speed in [m/s]',
#                 'Time blocking':'Monthly',
#                 'Direction binning':'centered',
#                 'Direction interval': 45.,
#                 'display':'On',
#                 'folder out':'/tmp/'})

# df=df[0].StatPlots.BIAS_histogramm(measured='Spd',modelled='Dir')#,\
#         # args={'Title':'Current speed',\
#         # 'units':'m/s',\
#         # 'Speed bins (optional)':[],
#         # '% quadran (optional)':[],
#         # 'Time blocking':'Annual',
#         # 'folder out':'/tmp/',
#         # })

# df=df[0].StatPlots.density_diagramm(X='Ve',Y='Dir',args={
#         'Y name':'',
#         'X name':'',
#         'Y unit':'',
#         'X unit':'',
#         'X limits':[0,np.inf],
#         'Y limits':[0,np.inf],
#         'folder out':'/tmp/'})


# df=df[0].StatPlots.QQ_plot(measured='Ve',modelled='Vn',args={
#         'measured name':'',
#         'modelled name':'',
#         'measured unit':'',
#         'modelled unit':'',
#         'Quantile increment step (%)':1.0,
#         'folder out':'/tmp/'})


# df=df[0].Statistics.wave_population(Hs='Spd',Tm02='Spd',Drr_optional='Dir',Tp_optional='Spd',SW_optional='Spd',\
#             args={'Method':'Height only',#:True,'Height/Direction':False,'Height/Tp':False,'height/period':False},
#                 'Direction binning':'centered',
#                 'Direction interval': 45.,
#                 'Heigh bin size': 0.1,
#                 'Period bin size': 2,
#                 'Exposure (years) (= length of time series if not specified)':0,
#                 'folder out':'',
#                 'Directional switch':'On'}
#             )



# df=df[0].WaveAnalysis.wave_spectra_plot(sea_level='Ve',\
#         args={'units':'m',
#          'Windows': 3600*24.,
#          'Overlap':1800*24.,
#          'Nfft':3600*24.,
#          'Detrend':'default', #:True,'linear':False,'constante':False},
#          'Period (s) min and max for plotting':[10*360, 1000],
#          'Xaxis':'frequency',#{'period':True,'frequency':False}
#          'folder out':'/tmp/',
#          'display':'On'#{'On':True,'Off':False}
#          })
df=df[0].WaveAnalysis.wavelet_analysis(sea_level='ssh',\
        args={
         'units':'m',
         'Mother wavelet':'Morlet',#:True,'Paul':False,'DOG':False},
         'Wave period range (min and max) (in s)':[3, 25],
         'Number of sub-ocatve per period band': 8,
         'Sea-level graphs':'On',#:True,'Off':True},
         'Scale-avgeraged wavelet power time series':'On',#:True,'Off':True},
         'folder out':os.getcwd(),
         'display':'On',#:True,'Off':False}
         })

# df=df[0].WaveAnalysis.ssh_to_wave_with_0crossing(sea_level='ssh',\
#         args={
#          'Windows': 3600.,
#          'Overlap':1800.,
#          'Nfft':3600.,
#          'Crossing':'Downcrossing', #:True,'linear':False,'constante':False},
#          'Wave period range (min and max) (in s)':[3, 25],
#          'Minimum number of waves per window for zero crossing analysis':30
#          })

# df=df[0].WaveAnalysis.ssh_to_wave_with_0crossing(sea_level='ssh',\
#         args={
#          'Windows': 3600.,
#          'Overlap':1800.,
#          'Nfft':3600.,
#          'Crossing':'Downcrossing', #:True,'linear':False,'constante':False},
#          'Wave period range (min and max) (in s)':[3, 25],
#          'Minimum number of waves per window for zero crossing analysis':30
#          })


# df=df[0].WaveAnalysis.ssh_to_wave_with_spectra(sea_level='ssh',\
#         args={'units':'m',
#          'Windows': 3600.,
#          'Overlap':1800.,
#          'Nfft':3600.,
#          'Detrend':'default', #:True,'linear':False,'constante':False},
#          'Wave period range (min and max) (in s)':[3, 25],
#          })

import pdb;pdb.set_trace()
sys.exit(-1)


import glob
filename=glob.glob('../test/1D_spec/*.NONDIRSPEC')
tx=TRYAXISfile(filename)
df=tx._toDataFrame()
data=TotoFrame()
data.add_dataframe(df,filename)
data.combine_dataframe(list(data.keys()))


#totoView.main(dataframes=[data['combined1']['dataframe']])



import xarray as xr

from wavespectra.specarray import SpecArray
from wavespectra.specdataset import SpecDataset

coords = {'time': [df[0]['time'][0]],
          'freq': df[0]['freq'],
          }

Z=df[0]['density'].values
#import pdb;pdb.set_trace()

efth = xr.DataArray(data=np.tile(Z,(1,1)),
                    coords=coords,
                    dims=('time','freq'),
                    name='efth')

dset = efth.to_dataset()

print(dset.spec.hs().values[0])
