
import pandas as pd
import numpy as np
np.warnings.filterwarnings('ignore')
from toto.core.attributes import attrs
from toto.core.metadataframe import MetadataFrame
import os
import copy
from matplotlib.dates import date2num,num2date


def sort_dataset(df,**args):
    df.sort_index(inplace=True,**args)
    return df

def get_freq(df):
    dt=(df.index[2]-df.index[1]).seconds
    return dt

def filled_gap(df,missing_value=np.NaN):

    df=sort_dataset(df)
    dt=get_freq(df)
    idx = pd.period_range(min(df.index), max(df.index),freq='%is'%dt)
    idx=idx.to_timestamp()

    df=df.reindex(idx,method='nearest', fill_value=missing_value,tolerance=dt)
    df.index.name='time' 
    return df

class TotoFrame(dict):


    def __init__(self,dataframe=None,filename=None):
        if dataframe:
            if type(dataframe) != type(list()):
                dataframe=[dataframe]
                self.add_dataframe(self,dataframe,filename)

    def _get_filename(self,dataframe,prefix):
      

        n0=len(self.keys())
        filename=[]
        if len(prefix)==1:
            prefix=prefix[0]
            prefix=os.path.split(prefix)[-1]
            for i in range(n0+1,len(dataframe)+n0+1):
                file='%s%i' % (prefix,i)
                self[file]={}
                filename.append(file)
        elif type(prefix)==type(list()):   
            for i in range(n0+1,len(dataframe)+n0+1):
                pref=os.path.split(prefix[i-1])[-1]
                file='%s%i' % (pref,i)
                self[file]={}
                filename.append(file)

        return filename

    def add_dataframe(self,dataframe,filename,metadataframe=MetadataFrame):
        filename=self._get_filename(dataframe,filename)
        for i,data in enumerate(dataframe):
            self[filename[i]]['metadata']={}
            for key in data.keys():
                self[filename[i]]['metadata'].update(metadataframe(key))
                if hasattr(data[key],'units'):
                    self[filename[i]]['metadata'][key]['units']=data[key].units
                if hasattr(data[key],'long_name'):
                    self[filename[i]]['metadata'][key]['long_name']=data[key].long_name
            if data.index.name=='time':
                data=filled_gap(data)

            self[filename[i]]['dataframe']=data
            self[filename[i]]['BACKUPdataframe']=copy.deepcopy(data)

        return filename
    def del_file(self,filename):
        del self[filename]

    def del_var(self,filename,variable,delete_metadata=True):


        del self[filename]['dataframe'][variable]
        if delete_metadata:
            del self[filename]['metadata'][variable]

    def move_metadata(self,fTo,fFrom,var):
        self[fTo]['metadata'][var]=self[fFrom]['metadata'].pop(var)
        return fTo,fFrom

    def move_var(self,fTo,fFrom,var,methods='nearest'):
        df=copy.deepcopy(self[fFrom]['dataframe'])
        tmp=df.reindex(self[fTo]['dataframe'].index,method=methods)
        self[fTo]['dataframe'][var]=tmp[var]
        self.del_var(fFrom,var,delete_metadata=False)
        self.move_metadata(fTo,fFrom,var)


    def delete_data(self,filename,varname,xlim=None,ylim=None):

        if self[filename]['dataframe'].index.name=='time':
            xdata=date2num(self[filename]['dataframe'].index)
        else:
            xdata=self[filename]['dataframe'].index


        if xlim and ylim:
            mask = ((xdata>= xlim[0]) & (xdata<= xlim[1])) &\
             ((self[filename]['dataframe'][varname]>= ylim[0]) & (self[filename]['dataframe'][varname]<= ylim[1]))

        
        self[filename]['dataframe'].loc[mask,varname]=np.NaN


    def reset(self,filename,varname=None):
        if varname:
            self[filename]['dataframe'][varname]=self[filename]['BACKUPdataframe'][varname]
        else:
            self[filename]['dataframe']=copy.depcopy(self[filename]['BACKUPdataframe'])






#### TESTING ###
if __name__ == '__main__':
    meta_df=TotoFrame(pd.DataFrame(abs(randn(3,3))),filename='test')#, index=['A','B','C'], columns=['c11','c22', 'c33']) 
    print(meta_df['test1']['metadata'][0])