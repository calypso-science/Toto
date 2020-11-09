import os,sys
import numpy as np
import pandas as pd
from toto.core.totoframe import TotoFrame
import toto
from toto.inputs.txt import TXTfile
from toto.inputs.mat import MATfile


from toto.core.cyclone_mask import Cyclone,binaries_directory
CYCLONE_FILE=os.path.join(binaries_directory(),'IBTrACS.ALL.v04r00.nc')

filename=r'_tests/txt_file/GSB.txt'
tx=TXTfile([filename],colNamesLine=1,skiprows=1,unitNamesLine=0,time_col_name={'year':'year','month':'month','day':'day','hour':'hour','min':'Minute'})
tx.reads()
tx.read_time()
df=tx._toDataFrame()
cy=Cyclone(cyclone_file=CYCLONE_FILE)
cy.limit_categories_within_radius([3,-1])

#sys.exit(-1)
msk=cy.remove_cyclones(df[0].index,[3,-1])
print(msk)
df[0]=df[0].loc[~msk]
print(df[0])