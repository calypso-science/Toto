#!/usr/bin/env python
"""
Percentage of occurence example
===============================
"""
import pandas as pd
import toto
import matplotlib.pyplot as plt
from toto.inputs.txt import TXTfile
import os
# read the file
hindcast='https://raw.githubusercontent.com/calypso-science/Toto/master/_tests/txt_file/tahuna_hindcast.txt'
os.system('wget %s ' % hindcast)

hd=TXTfile(['tahuna_hindcast.txt'],colNamesLine=1,skiprows=1,unitNamesLine=0,time_col_name={'Year':'year','Month':'month','Day':'day','Hour':'hour','Min':'Minute'})
hd.reads()
hd.read_time()
hd=hd._toDataFrame()

# # Processing
hd[0].StatPlots.percentage_of_occurence(mag='hs',drr='dpm',args={
                'magnitude interval (optional)':[],
                'X label':'Significant wave height in m',
                'time blocking':'Annual',
                'direction binning':'centered',
                'direction interval': 90.,
                'display':'On'})
