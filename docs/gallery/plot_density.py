#!/usr/bin/env python
"""
Density histogramm examples
===========================
"""
import pandas as pd
import toto
import matplotlib.pyplot as plt
from toto.inputs.txt import TXTfile
import os
# read the file
hindcast='https://raw.githubusercontent.com/calypso-science/Toto/master/_tests/txt_file/tahuna_hindcast.txt'
measured='https://raw.githubusercontent.com/calypso-science/Toto/master/_tests/txt_file/tahuna_measured.txt'
os.system('wget %s ' % hindcast)
os.system('wget %s ' % measured)

hd=TXTfile(['tahuna_hindcast.txt'],colNamesLine=1,skiprows=1,unitNamesLine=0,time_col_name={'Year':'year','Month':'month','Day':'day','Hour':'hour','Min':'Minute'})
hd.reads()
hd.read_time()
hd=hd._toDataFrame()

# # Processing
hd[0].StatPlots.density_diagramm(X='tp',Y='hs',args={
        'X name':'Wave period',
        'Y name':'Significant wave height',
        'Y unit':'m',
        'X unit':'s',
        'Y limits':[0,5],
        'X limits':[0,20],
        'display':'On',
        })
