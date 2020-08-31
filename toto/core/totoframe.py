
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
    dt=(df.index[2]-df.index[1]).total_seconds()
    return dt

def filled_gap(df,missing_value=np.NaN):

    df=sort_dataset(df)
    dt=get_freq(df)
    
    #dt=(dt + 9) // 10 * 10
    dt=np.round(dt*1000)
    idx = pd.period_range(min(df.index), max(df.index),freq='%ims'%dt)
    idx=idx.to_timestamp()

    df0=pd.DataFrame(index=idx)
    df0.index.name='time'
    del df['time']
    tol=int(dt*2)
    df=pd.merge_asof(df0,df,on='time',direction='nearest', tolerance=pd.Timedelta("%ims"%tol)).set_index('time',drop=False)

    #df=df.reindex(idx,method='nearest', fill_value=missing_value,tolerance=3600)
    df.index.name='time' 
    return df
def add_metadata_to_df(df,metadata):
    for key in metadata:
        for subkey in metadata[key]:
            setattr(df[key],subkey,metadata[key][subkey])
    return df

class TotoFrame(dict):


    def __init__(self,dataframe=[],filename=[]):
        if len(dataframe)>0:
            if type(dataframe) != type(list()):
                dataframe=[dataframe]
                self.add_dataframe(dataframe,filename)

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
                pref=os.path.split(prefix[i-1-n0])[-1]
                file='%s%i' % (pref,i)
                self[file]={}
                filename.append(file)

        return filename

    def add_dataframe(self,dataframe,filename,metadataframe=MetadataFrame,change_name=True):
        if change_name:
            filename=self._get_filename(dataframe,filename)
        else:
            for file in filename:
                self[file]={}
        for i,data in enumerate(dataframe):
            self[filename[i]]['metadata']={}
            for key in data.keys():
                self[filename[i]]['metadata'].update(metadataframe(key))
                if hasattr(data[key],'units'):
                    self[filename[i]]['metadata'][key]['units']=data[key].units
                if hasattr(data[key],'long_name'):
                    self[filename[i]]['metadata'][key]['long_name']=data[key].long_name

            if hasattr(data,'longitude'):
                self[filename[i]]['longitude']=data.longitude
                self[filename[i]]['latitude']=data.latitude
            else:
                self[filename[i]]['longitude']=None
                self[filename[i]]['latitude']=None

            if data.index.name=='time':
                data=filled_gap(data)

            self[filename[i]]['dataframe']=data
            self[filename[i]]['BACKUPdataframe']=copy.deepcopy(data)
            self[filename[i]]['BACKUPmetadata']=copy.deepcopy(self[filename[i]]['metadata'])
        return filename

    def replace_dataframe(self,filename,dataframe):
        self.del_file(filename)
        self.add_dataframe(dataframe,filename,change_name=False)


    def del_file(self,filename):
        if not isinstance(filename,list):
            filename=[filename]

        for file in filename:
            del self[file]

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
        if varname is None:
            self[filename]['dataframe']=copy.deepcopy(self[filename]['BACKUPdataframe'])
            self[filename]['metadata']=copy.deepcopy(self[filename]['BACKUPmetadata'])
        else:
            self[filename]['dataframe'][varname]=self[filename]['BACKUPdataframe'][varname]
            self[filename]['metadata'][varname]=self[filename]['BACKUPmetadata'][varname]
        
            

    def combine_dataframe(self,filenames):

        df0=self[filenames[0]]['dataframe'].copy()
        df0.set_index('time',inplace=True,drop=False)
        self.del_file(filenames[0])
        del filenames[0]
        for file in filenames:
            tmp=self[file]['dataframe'].copy()
            tmp.set_index('time',inplace=True,drop=False)
            df0=df0.append(tmp)
            self.del_file(file)

        #df0.set_index(['time', 'freq'], inplace=True,drop=False)
        df0.set_index('time', inplace=True,drop=False)
        self.add_dataframe([df0],['combined'])






#### TESTING ###
if __name__ == '__main__':
    meta_df=TotoFrame(pd.DataFrame(abs(randn(3,3))),filename='test')#, index=['A','B','C'], columns=['c11','c22', 'c33']) 
    print(meta_df['test1']['metadata'][0])