#!/usr/bin/env python
"""
Wave spectra examples
=====================
"""
import os
import pandas as pd
import toto


wavefile='https://raw.githubusercontent.com/calypso-science/Toto/master/_tests/txt_file/yura87.dat'
os.system('wget %s ' % wavefile)

wave=pd.read_csv('yura87.dat',skiprows=28,names=['time','ssh1','ssh2','ssh3'],delimiter='\s+')
time=pd.to_datetime(wave['time'],unit='s')
wave['time'][:]=time
wave.set_index('time',inplace=True)

wave.WaveAnalysis.wave_spectra(sea_level='ssh1',\
        args={'units':'m',
         'windows': 3600,
         'overlap':1800,
         'nfft':3600,
         'detrend':'Off',
         'period (s) min and max for plotting':[5, 250],
         'xaxis':'period',
         'display':'On',
         })

# wave.WaveAnalysis.wave_spectra(sea_level='ssh',\
#         args={'units':'m',
#          'windows': 3600,
#          'overlap':1800,
#          'nfft':3600,
#          'detrend':'Off',
#          'period (s) min and max for plotting':[3, 250],
#          'xaxis':'frequency',
#          'display':'On',
#          })
