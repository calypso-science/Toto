import os,sys
import toto
from toto.inputs.txt import TXTfile
import numpy as np
import pandas as pd


filename=os.path.join('txt_file','cyclones_115.3085_19.8892.txt')
tx=TXTfile([filename],colNamesLine=1,skiprows=1,unitNamesLine=0,time_col_name={'Year':'year','Month':'month','Day':'day','H[UTC]':'hour','Min':'Minute'})
tx.reads()
tx.read_time()
df=tx._toDataFrame()[0]
df.filename='test'
df.StatPlots.density_diagramm(X='hs',Y='tp',args={
        'Y name':'Period',
        'X name':'Hs',
        'Y unit':'s',
        'X unit':'m',
        'X limits':[0,np.inf],
        'Y limits':[0,np.inf],
        'display': 'Off' ,
        'folder out':os.getcwd()})


