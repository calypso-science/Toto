"""Output timeseries in NetCDF format.
"""
import glob,os,sys
import pandas as pd
import datetime as dt
import copy

def defaultExtensions():
    return ['.nc']

def NCfile(filename,datas):
    datas=copy.deepcopy(datas)
    fileout=copy.deepcopy(filename)
    for i,df in enumerate(datas):
        if len(datas)>1:
            fileout=filename[:-3]+str(i)+'.txt'
        del df['dataframe'][df['dataframe'].index.name]
        xar=df['dataframe'].to_xarray()

        cols=list(df['dataframe'].columns)
        for i,col in enumerate(cols):
            attr={}
            uni=df['metadata'][col]['units']
            if uni and uni!='None':
                attr['units']=uni

            uni=df['metadata'][col]['long_name']
            if uni and uni!='None':
                attr['long_name']=uni            

            xar[col].attrs=attr


        xar.to_netcdf(path=fileout, mode='w')

