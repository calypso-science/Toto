"""Write generic mat files.
"""
import glob,os,sys
import pandas as pd
import datetime as dt
import copy
import scipy.io as sio

def defaultExtensions():
    return ['.mat']

def MATfile(filename,datas):
    datas=copy.deepcopy(datas)
    fileout=copy.deepcopy(filename)
    for i,df in enumerate(datas):
        if len(datas)>1:
            fileout=filename[:-3]+str(i)+'.mat'
        del df['dataframe'][df['dataframe'].index.name]
        # cols=list(df['dataframe'].columns)
        # for i,col in enumerate(cols):
        #     uni=df['metadata'][col]['units']
        #     if uni and uni!='None':
        #         cols[i]=col+'['+uni+']'

        # index_label=df['dataframe'].index.name
        # uni=df['metadata'][index_label]['units']
        # if uni and uni!='None':
        #     index_label=index_label+'['+uni+']'
        
        sio.savemat(fileout, {name: col.values for name, col in df.items()})
