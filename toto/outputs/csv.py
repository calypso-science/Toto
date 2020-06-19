"""Write generic txt files.
"""
import glob,os,sys
import pandas as pd
import datetime as dt
import copy

def defaultExtensions():
    return ['.csv']

def CSVfile(filename,datas):
    datas=copy.deepcopy(datas)
    fileout=copy.deepcopy(filename)
    for i,df in enumerate(datas):
        if len(datas)>1:
            fileout=filename[:-3]+str(i)+'.txt'
        del df['dataframe'][df['dataframe'].index.name]
        cols=list(df['dataframe'].columns)
        for i,col in enumerate(cols):
            uni=df['metadata'][col]['units']
            if uni and uni!='None':
                cols[i]=col+'['+uni+']'

        index_label=df['dataframe'].index.name
        uni=df['metadata'][index_label]['units']
        if uni and uni!='None':
            index_label=index_label+'['+uni+']'
        df['dataframe'].to_csv(fileout,header=cols,index_label=index_label, sep='\t',index=True)
