"""Read generic netcdf file

"""
import glob,os,sys
import pandas as pd
import xarray as xr
import numpy as np

class MOETfile():

    @staticmethod
    def defaultExtensions():
        return ['.nc']


    def __init__(self,filenames):

        if isinstance(filenames,str):
            filenames=[filenames]
        self.filenames=filenames
        self.data=[]
        # READ 
        self._reads_nc()

    def _reads_nc(self):
        for file in self.filenames:
            self._read_nc(file)

    def _read_nc(self,filename):

        ds = xr.open_dataset(filename)

        D1_keys=[]
        D2_keys=[]
        key_to_drop=[]
        for key in ds.keys():
            if 'records' in ds[key].dims:
                # if 'lev' in ds[key].dims:
                #     D2_keys.append(key)
                # else:
                D1_keys.append(key)

            else:
                key_to_drop.append(key)

        ds.drop_vars(key_to_drop)

        df = ds.to_dataframe()


        df0=[]
        if len(D2_keys)>0:
            nlev=df.index.get_level_values('lev').unique()
            for m in nlev:
                df2d=df[D2_keys].loc[(m)]
                df2d.reset_index(inplace=True)
                df2d.set_index('time',inplace=True)
                df2d=df2d.add_suffix('_lev_'+str(m))
                df0.append(df2d)
              
        if len(D1_keys)>0:
                df1d=df[D1_keys]
                t0=df1d['Time'][:,0]
                t1=df1d['Time'][:,1]
                year=np.floor(t0/10000).astype(int)
                month=np.floor((t0-(year*10000))/100).astype(int)
                day=np.floor((t0-(year*10000)-(month*100))/1).astype(int)
                tt=pd.to_datetime({'Year':year,'Month':month,'Day':day})+pd.to_timedelta(t1,'ms')
                del df1d['Time']
                df1d.reset_index(inplace=True)
                df1d=df1d.drop_duplicates(subset='records').set_index('records')
                del df1d['timedim']
                # 
                df1d['time']=tt
                df1d.reset_index(inplace=True)
                df1d.set_index('time',inplace=True)
                del df1d['records']


                df0.append(df1d)

        df0=pd.concat(df0,axis=1)
        df0.reset_index(inplace=True)
        df0.set_index('time',inplace=True,drop=False)
        columns=df0.columns

        for col in list(df0.columns):
            if '_lev_' in col:
                Col=col.split('_lev_')[0]
            elif col=='time':
                continue
            else:
                Col=col
            if hasattr(ds[Col],'units'):
                setattr(df0[col],'units',ds[Col].units)
            if hasattr(ds[Col],'long_name'):
                setattr(df0[col],'long_name',ds[Col].long_name)


        if 'Longitude' in ds:
            setattr(df0,'longitude',ds['Longitude'].values)
            setattr(df0,'latitude',ds['Latitude'].values)
        self.data.append(df0)




    def _toDataFrame(self):
       #print(self.data)
        return self.data




if __name__ == '__main__':
    MOETfile('/home/remy/Downloads/dep1/77686_October_77686.nc')