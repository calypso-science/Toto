import os,sys
import toto
from toto.inputs.mat import MATfile
from toto.inputs.cons import CONSfile
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

filename=r'mat_file/tidal.mat'
tx=MATfile(filename)
df=tx._toDataFrame()
df[0].filename='sss'
df[0]['e']=df[0]['el_res']+df[0]['el_tide']

# Remove tide
tide=df[0].TideAnalysis.detide(
               mag='e',
               args={'minimum SNR':2,
                     'latitude':-36.0,
                     'folder out':os.getcwd(),
                     })
plt.figure()
plt.plot(df[0].index,df[0]['e'],label='total')
plt.plot(tide.index,tide['et'],label='tide')
plt.plot(tide.index,tide['eo'],label='residual')
plt.legend()
plt.show(False)

# Predict tide
new=df[0].TideAnalysis.predict(
                mag='e',
                args={'minimum time':datetime.datetime(2020,1,1),
                	  'maximum time':datetime.datetime(2020,2,1),
                	  'dt(s)':3600,
                      'minimum SNR':2,'trend': False,
                      'latitude':-36.0,
                })

plt.figure()
plt.plot(new.index,new['et'],label='tide')
plt.show(False)

## Tidal stats
df[0].TideAnalysis.tidal_stat(mag='el_tide',\
        args={'minimum SNR':2,\
        'latitude':-36.0,
        'folder out':os.getcwd(),
        })

# Skew surge
skew=df[0].TideAnalysis.skew_surge(
                   mag='el_tide',
                   args={'minimum SNR':2,
                        'latitude':-36.0})
plt.figure()
plt.plot(df[0].index,df[0]['el_tide'],label='raw')
plt.plot(skew.index,skew['skew_surge_magnitude'],label='skew_surge_magnitude')
plt.plot(skew.index,skew['skew_surge_lag'],label='skew_surge_lag')
plt.plot(skew.index,skew['tidal_elevation_maximum_over_tidal_cycle'],label='tidal_elevation_maximum_over_tidal_cycle')
plt.plot(skew.index,skew['total_water_level_maximum_over_tidal_cycle'],label='total_water_level_maximum_over_tidal_cycle')
plt.legend()
plt.show(False)

# read cons from a file
filename=r'cons/cons_list.csv'

cons=CONSfile([filename],sep=',',\
                           colNames=[],\
                           unit='degrees',\
                           miss_val='NaN',\
                           colNamesLine=1,\
                           skiprows=1,\
                           skipfooter=0,\
                           col_name={'cons':'Cons',
                                     'amp':'Amplitude',
                                     'pha':'Phase'},\
                           )
cons.reads()
cons.read_cons() 
df=cons._toDataFrame()
print(df)
plt.figure()
plt.plot(df[0].index,df[0]['tide'],label='tide')
plt.show()
