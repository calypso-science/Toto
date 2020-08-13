import os,sys
from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QApplication
sys.path.append(r'/home/remy/Calypso/Projects/004_Toto/Toto')
from totoview.dialog.message import wrapper_plugins
import toto
import pandas as pd
import numpy as np
app = QApplication(sys.argv)

dates = pd.date_range('1/1/2000', periods=360)
arr=np.random.randn(360, 8)
arr[:,0]=15.2 # water depth
arr[:,1]=-5.3 # U
arr[:,2]= 6.2 # V
arr[:,3]= 1.5 # Hs
arr[:,4]= 0.5 # Hs_sw
arr[:,5]= 15 # Tp
arr[:,6]= 1.8 # ws
arr[:,7]= 150 # drr
df = pd.DataFrame(arr,index=dates, columns=['Depth','U', 'V', 'Hs','Hs_sw','Tp','spd','drr'])
df.index.name='time'
#tf=TotoFrame(dataframe=df,filename=['test'])

sc=wrapper_plugins([df],toto.plugins.transformations.calc_spdir)
sc.exec_()