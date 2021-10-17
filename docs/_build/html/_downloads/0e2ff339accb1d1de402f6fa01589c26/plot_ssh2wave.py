#!/usr/bin/env python
"""
Sea level to wave examples
==========================
"""
import os
import pandas as pd
import toto
import matplotlib.pyplot as plt

wavefile='https://raw.githubusercontent.com/calypso-science/Toto/master/_tests/txt_file/yura87.dat'
os.system('wget %s ' % wavefile)

wave=pd.read_csv('yura87.dat',skiprows=28,names=['time','ssh1','ssh2','ssh3'],delimiter='\s+')
time=pd.to_datetime(wave['time'],unit='s')
wave['time'][:]=time
wave.set_index('time',inplace=True)

### Using the spectral method
result=wave.WaveAnalysis.ssh_to_wave(sea_level='ssh1',\
        args={
         'windows': 3600,
         'overlap':1800,
         'nfft':3600,
         'detrend':'Off',
         'wave period range (min and max) (in s)':[3, 25],
         'method':'spectra',
         'minimum number of waves per window for zero crossing analysis': 30,
         })

print(result)

### Using the zero-crossing method
result2=wave.WaveAnalysis.ssh_to_wave(sea_level='ssh1',\
        args={
         'windows': 3600,
         'overlap':1800,
         'nfft':3600,
         'detrend':'Off',
         'wave period range (min and max) (in s)':[3, 25],
         'method':'zero-crossing',
         'minimum number of waves per window for zero crossing analysis': 30,
         })

print(result2)

# Plot the results
fig=plt.figure()
ax = plt.subplot(211)
plt.plot(result.index,result['Hs'],'b-',label='spectra method')
plt.plot(result.index,result2['hs'],'r-',label='zero-crossing method')
ax.set_ylabel('Hs [m]')
ax.legend()
fig.autofmt_xdate()

ax = plt.subplot(212)
plt.plot(result.index,1/result['fmax'],'b-',label='spectra method (Tp)')
plt.plot(result.index,result2['ts'],'r-',label='zero-crossing method (Ts)')
ax.set_ylabel('Period [s]')
ax.legend()
fig.autofmt_xdate()

plt.show()