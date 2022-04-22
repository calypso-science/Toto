import os,sys
import toto
from toto.inputs.mat import MATfile
import numpy as np
import pandas as pd

filename=os.path.join('mat_file','F3.mat')
tx=MATfile(filename)
df=tx._toDataFrame()
df[0].filename='test'
df=df[0].Statistics.common_statistics(mag='spd',drr='drr')#,args={'time blocking':'yearly'})
