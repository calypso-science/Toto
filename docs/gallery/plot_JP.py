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
hd[0].StatPlots.joint_probability_plot(Y='hs',X='tp',\
        args={    
        'X Min Res Max(optional)':[2,1,22],
        'Y Min Res Max(optional)':[0,0.5],
        'X label':'Wave Period [s]',
        'Y label':'Wave height [m]',
        'time blocking':'Seasonal (South hemisphere)',
        'probablity expressed in':'percent',
        'display':'On',
        })