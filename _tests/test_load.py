import os,sys
import numpy as np
import pandas as pd
from toto.inputs.txt import TXTfile


filename=r'test.csv'
tx=TXTfile([filename],colNamesLine=1,miss_val='NaN',sep=',',skiprows=1,unit='custom',time_col_name='time',unitNamesLine=0,single_column=True,customUnit='%d/%m/%Y %H:%M')
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