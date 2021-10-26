#!/usr/bin/env python
"""
Create bed shear stress example
===============================
"""
import pandas as pd
import toto
import matplotlib.pyplot as plt
from toto.inputs.txt import TXTfile
import os
# read the file
hindcast='https://raw.githubusercontent.com/calypso-science/Toto/master/_tests/txt_file/wave_currents.txt.csv'
os.system('wget %s ' % hindcast)

hd=TXTfile(['wave_currents.txt.csv'],colNamesLine=1,skiprows=1,unitNamesLine=0,time_col_name={'year':'year','month':'month','day':'day','hour':'hour','min':'Minute'})
hd.reads()
hd.read_time()
hd=hd._toDataFrame()


#%%
#Switch from U and V to spd an drr
hd[0]['spd']=hd[0].DataTransformation.uv_to_spddir(u='Ve',v='Vn')['spd']

#%%
#Calculate bed shear stress
bed_shear=hd[0].DataTransformation.bed_shear_stress(spd='spd',hs='hs',tp='tp',
                        args={'mode':'3D',
                        'water_depth':10,
                        'rho_water':1027,
                              'z0': 0.001,
                        })

#%% Plot the results
fig=plt.figure()
ax1 = plt.subplot(211)
ax1.plot(hd[0].index,hd[0]['spd'],'b',label='Current speed')
ax1.set_ylabel('Current speed [m/s]',color='b')
ax1.tick_params(axis='y', color='b', labelcolor='b')
ax1bis = ax1.twinx()
ax1bis.plot(hd[0].index,hd[0]['hs'],'r',label='Wave height')
ax1bis.set_ylabel('Wave height [m]',color='r')
ax1bis.tick_params(axis='y', color='r', labelcolor='r')
fig.autofmt_xdate()

ax2 = plt.subplot(212)
p1=ax2.plot(bed_shear.index,bed_shear['tau_cw'],'b',label='Mean bed shear stress during wave cycle')
ax2.set_ylabel('Mean bed shear stress [N/m2]',color='b')
ax2.tick_params(axis='y', color='b', labelcolor='b')

ax2bis = ax2.twinx()
p2=ax2bis.plot(bed_shear.index,bed_shear['tau_cw_max'],'r',label='Maximum bed shear stress during wave cycle')
ax2bis.tick_params(axis='y', color='r', labelcolor='r')
ax2bis.set_ylabel('Max bed shear stress [N/m2]',color='r')

fig.autofmt_xdate()
plt.tight_layout()
plt.show()
