#!/usr/bin/env python
"""
Wavelet examples
================
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


wave.WaveAnalysis.wavelet_analysis(sea_level='ssh1',\
        args={
         'units':'m',
         'mother wavelet':'Morlet',
         'wave period range (min and max) (in s)':[3, 25],
         'number of sub-ocatve per period band': 8,
         'display':'On'
         })
