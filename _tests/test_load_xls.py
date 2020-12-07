import os,sys
import numpy as np
import pandas as pd
from toto.inputs.xls import XLSfile


filename=r'/home/remy/Calypso/Software/TOTO/Toto/_tests/xls_file/data.xlsx'
#tx=XLSfile([filename],sheetnames='test1',skiprows=0,time_col_name={'Year':'year','Month':'month','Day':'day','Hour [UTC]':'hour','Minute':'minute'})
tx=XLSfile([filename],sheetnames='test3', colNames= [], unitNames= [],miss_val='NaN', colNamesLine= 1, skiprows= 2, unitNamesLine= 0, skipfooter= 0,\
 single_column= True, unit= 's', customUnit= '%d-%m-%Y %H:%M:%S', time_col_name= {})

tx.reads()
print(tx.data)
tx.read_time()
df=tx._toDataFrame()
print(df)

