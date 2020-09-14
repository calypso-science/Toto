import os,sys
sys.path.append('/home/remy/Software/Toto')
sys.path.append('/home/remy/Calypso/Projects/004_Toto/Toto')
import numpy as np
import pandas as pd
from toto.core.totoframe import TotoFrame
import toto

from toto.inputs.msl import MSLfile

filename=r'../for_remy/marjan_all.nc'
tx=MSLfile([filename])
df=tx._toDataFrame()
