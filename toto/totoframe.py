
import pandas as pd
import numpy as np
from toto.core.attributes import attrs
from toto.core.metadataframe import MetadataFrame
import os

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
    df=df.reindex(idx, fill_value=missing_value)
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
            for key in data:
                self[filename[i]]['metadata'].update(metadataframe(key))
                if hasattr(data[key],'units'):
                    self[filename[i]]['metadata'][key]['units']=data[key].units
                if hasattr(data[key],'long_name'):
                    self[filename[i]]['metadata'][key]['long_name']=data[key].long_name
            if data.index.name=='time':
                data=filled_gap(data)

            self[filename[i]]['dataframe']=data

    def del_file(self,filename):
        del self[filename]

    def del_var(self,filename,variable,delete_metadata=True):
        del self[filename]['dataframe'][variable]
        if delete_metadata:
            del self[filename]['metadata'][variable]

    def move_metadata(fTo,fFrom,var):
        self[fTo]['metadata']=self[fFrom]['metadata'].pop(var)
        return dfIn,dfOut

    def move_var(self,fTo,fFrom,var,methods='exactly'):
        if methods is 'exactly':
            self[fTo]['dataframe'][var]=self[fTo]['dataframe'].index(self[fFrom]['dataframe'][var])
            self.del_var(fTo,var,delete_metadata=False)
        else:
            pass

        self.move_metadata(fTo,fFrom,var)





#### TESTING ###
if __name__ == '__main__':
    meta_df=TotoFrame(pd.DataFrame(abs(randn(3,3))),filename='test')#, index=['A','B','C'], columns=['c11','c22', 'c33']) 
    print(meta_df['test1']['metadata'][0])