import os,sys
sys.path.append(r'/home/remy/Calypso/Projects/004_Toto/Toto')
import numpy as np
import pandas as pd
#from toto.core.totoframe import TotoFrame
import toto
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
#tf=TotoFrame(dataframe=df,filename=['test'])
tf={}
tf['test1']={}
tf['test1']['dataframe']=df
df=tf['test1']['dataframe'].DataTransformation.calc_spdir(u='U',v='V')
print(df)
print('speed=%.2f and drr=%.2f' %(df['spd'][0],df['drr'][0]))

df=tf['test1']['dataframe'].DataTransformation.calc_uv(spd='spd',direc='drr')
print('u=%.2f and v=%.2f' %(df['u'][0],df['v'][0]))

sys.exit(-1)
Hs=tf['test1']['dataframe'].trans.hs_sea(hs='Hs',hs_swell='Hs_sw')
print('Hs sea=%.2f' %(Hs[0]))
Uorb=tf['test1']['dataframe'].trans.Uorb(dp='Depth',tp='Tp',hs='Hs',z=0)
print('Uorb=%.2f' %(Uorb[0]))
ly=tf['test1']['dataframe'].trans.dav2layers(u='U',dp='Depth')
print('U0=%.2f' %(ly[0]))
ly=tf['test1']['dataframe'].trans.layers2dav(u='U',dp='Depth')
print('Um=%.2f' %(ly[0]))
ly=tf['test1']['dataframe'].trans.windprofile(ws='spd',opts={'Output level (in meters)':200})
print('Wspd=%.2f' %(ly[0]))