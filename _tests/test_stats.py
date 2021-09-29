import os,sys
sys.path.append('/home/remy/Software/Toto')
sys.path.append('/home/remy/Calypso/Projects/004_Toto/Toto')
import numpy as np
import pandas as pd
from toto.core.totoframe import TotoFrame
import toto
from toto.inputs.txt import TXTfile
from toto.inputs.mat import MATfile

from toto.inputs.msl import MSLfile
from toto.plugins.wave._do_ssh_to_wave import zero_crossing
from toto.filters.bandpass_filter import bandpass_filter

# filename=r'_tests/txt_file/GSB.txt'
# tx=TXTfile([filename],colNamesLine=1,skiprows=1,unitNamesLine=0,time_col_name={'year':'year','month':'month','day':'day','hour':'hour','min':'Minute'})
# tx.reads()
# tx.read_time()
# df=tx._toDataFrame()
# filename=r'../P1.txt'
# tx=TXTfile([filename],colNamesLine=1,skiprows=1,unitNamesLine=0,time_col_name={'Year':'year','Month':'month','Day':'day','H[UTC]':'hour','Min':'Minute'})
# tx.reads()
# tx.read_time()
# df=tx._toDataFrame()
# filename=r'_tests/nc_file/TB_current.nc'
# tx=MSLfile([filename])
# df=tx._toDataFrame()
# tx=TXTfile([filename],colNamesLine=1,skiprows=1,unitNamesLine=0,time_col_name={'Year':'year','Month':'month','Day':'day','H[UTC]':'hour','Min':'Minute'})
# tx.reads()
# tx.read_time()
# df=tx._toDataFrame()
#df[0].filename='sss'
filename=r'mat_file/F3.mat'
tx=MATfile(filename)
# tx=TXTfile([filename],colNamesLine=1,skiprows=1,unitNamesLine=0,time_col_name={'year':'year','month':'month','day':'day','hour':'hour','min':'Minute'})
# tx.reads()
# tx.read_time()
df=tx._toDataFrame()
df[0].filename='sss'
print(df)
# time=df[0].index
# mag=df[0]['ssh'].values

#caca=zero_crossing(pd.DataFrame(),time[0],time,mag,False,30)
# df=df[0].StatPlots.joint_probability_plot(Hs='hs[m]',Tm02='t02[s]',args={\
#     'folder out':os.getcwd(),'X Min Res Max(optional)':[0,2],'Y Min Res Max(optional)':[0,2],\
#     'Time blocking':'Monthly','Probablity expressed in':'percent','Probablity expressed in':'per thoushand','display':'On'})

df2=df[0].Statistics.weather_window(data='spd',args={'method':'exceedance non-persistence',\
  'folder out':'','Exceedance bins: Min Res Max(optional)':[0,0.5],'Duration Min Res Max':[6,6,12],
  'Time blocking':'Monthly'})
import pdb;pdb.set_trace()
# df=df[0].Statistics.weighted_direction(Hs='hs[m]',drr='dpm_sea8[deg]',args={'folder out':os.getcwd(),
#                                                     'type':'South hemisphere(Summer/Winter)'
#                                                             })

# df=df[0].Statistics.modal_wave_period(Hs='hs[m]',Tp='tp[s]',args={'folder out':os.getcwd(),
#                                                     'type':'South hemisphere(Summer/Winter)'
#                                                             })
#df=tf['test1']['dataframe'].Statistics.common_stats(mag='U',drr='drr')

# df=df[0].Woodside.joint_probability(speed='hs[m]',direction='dpm[deg]',period='tp[s]',args={'method':'Mag vs Per',\
# 	'folder out':os.getcwd(),'X Min Res Max(optional)':[2,2,20],'Y Min Res Max(optional)':[0,0.5],'Direction binning':'centred',\
# 	'Direction interval': 45.,'Time blocking':'Annual','Probablity expressed in':'percent'})

# df=df[0].Woodside.persistence_probability(data='hs[m]',args={'method':'non-exceedance',\
# 	'folder out':'','Exceedance bins: Min Res Max(optional)':[2,1],'Duration Min Res Max':[6,6,18],
# 	'Time blocking':'Annual','Probablity expressed in':'percent'})
# print(df[0])
# df=df[0].StatPlots.Plot_thermocline(mag=['temp_lev_0','temp_lev_5','temp_lev_10'],\
#         args={'X label':'Current speed',\
#         'function':'Max',
#         'Percentile or Quantile': 0.1,
#         'Time blocking':'Monthly',
#         'display':'On',
#         'folder out':os.getcwd(),
#         })
# df[0].Woodside.extreme_analysis(wind_speed10='hs[m]',wind_drr='dpm[deg]',
#                           hs='hs[m]',tp='tp[s]',tm02='t02[s]',dpm='dpm[deg]',
#                           surface_current='hs[m]',surface_drr='dpm[deg]',
#                           midwater_current='hs[m]',midwater_drr='dpm[deg]',
#                           bottom_current='hs[m]',bottom_drr='dpm[deg]',
#                           args={'return_period': [1,5,10,20,50,100,200,500,1000],
#                           'Display':'On',
#                           'Water depth':5000.,
#                           'Directional switch':'On',
#                           'folder out':os.getcwd(),
#                            })



# df[0].filename='test'
# df=df[0].Statistics.Directional_statistics(magnitude='Spd',direction='Dir',\
#         args={
#         'function':'Quantile',#{'Max':True, 'Mean':False, 'Median':False, 'Min':False, 'Percentile':False, 'Prod':False, 'Quantile':False, 'Std':False, 'Sum':False, 'Var':False},
#         'Percentile or Quantile': 0.1,
#         'folder out':os.getcwd(),
#         'Direction binning':'centered',
#         'Direction interval': 45.,
#         'Time blocking':'Monthly',#{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
#         })


# df=df[0].Statistics.exceedence_probability(data='hs[m]',args={'method':'exceedance persistence',\
# 	'folder out':'','Exceedance bins: Min Res Max(optional)':[0,0.1],'Duration Min Res Max':[1,1,12],
# 	'Time blocking':'Annual','Probablity expressed in':'percent'})

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
# df=df[0].WaveAnalysis.wavelet_analysis(sea_level='ssh',\
#         args={
#          'units':'m',
#          'Mother wavelet':'Morlet',#:True,'Paul':False,'DOG':False},
#          'Wave period range (min and max) (in s)':[3, 25],
#          'Number of sub-ocatve per period band': 8,
#          'Sea-level graphs':'On',#:True,'Off':True},
#          'Scale-avgeraged wavelet power time series':'On',#:True,'Off':True},
#          'folder out':os.getcwd(),
#          'display':'On',#:True,'Off':False}
#          })
#bandpass_filter(df[0]['ssh'],args={'lower cut-off':3,'upper cut-off':25})
# df=df[0].WaveAnalysis.ssh_to_wave(sea_level='ssh',\
#         args={
#          'Windows': 3600.,
#          'Overlap':1800.,
#          'Nfft':3600.,
#          'Crossing':'Downcrossing', #:True,'linear':False,'constante':False},
#          'Wave period range (min and max) (in s)':[3, 25],
#          'Minimum number of waves per window for zero crossing analysis':30,
#          'Method':'zero-crossing',
#          'Detrend':'Off',
#          })


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
