import os,sys
import numpy as np
import pandas as pd
from toto.inputs.xls import XLSfile


filename=r'../Raglan1.csv'
tx=TXTfile([filename],colNamesLine=1,miss_val='GAP',sep=',',skiprows=1,unitNamesLine=0,time_col_name={'2008':'year','7':'month','1':'day','13':'hour','5':'Minute','0':'second'})
tx.reads()
tx.read_time()
df=tx._toDataFrame()
print(df)
import pdb;pdb.set_trace()
tf=TotoFrame()
tf.add_dataframe(df,['caca'])
print(tf)
# df[0].filename='ff'
# df=df[0].TideAnalysis.detide(mag='TideLVL ',\
#         args={'Minimum SNR':2,\
#         'Latitude':-36.0,
#         'folder out':'/tmp/',
#         })

# print(df)