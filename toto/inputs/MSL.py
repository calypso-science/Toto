"""Read netcdf from MSL.

"""
import glob,os,sys
import pandas as pd
import xarray as xr


class MSLfile():

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

        D2_keys=[]
        D3_keys=[]
        key_to_drop=[]
        for key in ds.keys():
            if 'time' in ds[key].dims:
                if 'lev' in ds[key].dims:
                    D3_keys.append(key)
                else:
                    D2_keys.append(key)

            else:
                key_to_drop.append(key)

        ds.drop_vars(key_to_drop)

        df = ds.to_dataframe()


        sites=df.index.get_level_values('site').unique()

        for n in sites:
            df0=[]
            if len(D3_keys)>0:
                nlev=df.index.get_level_values('lev').unique()
                for m in nlev:
                    df3d=df[D3_keys].loc[(0,m,n)]
                    df3d.reset_index(inplace=True)
                    df3d.set_index('time',inplace=True)
                    df3d=df3d.add_suffix('_lev_'+str(m))
                    df0.append(df3d)
                  
            if len(D2_keys)>0:
                    df2d=df[D2_keys].loc[(0,n)]
                    df2d.reset_index(inplace=True)
                    df2d.set_index('time',inplace=True)
                    df0.append(df2d)

            df0=pd.concat(df0,axis=1)
            df0.reset_index(inplace=True)
            df0.set_index('time',inplace=True,drop=False)
            for col in list(df0.columns):
                if '_lev_' in col:
                    Col=col.split('_lev_')[0]
                else:
                    Col=col
                if hasattr(ds[Col],'units'):
                    setattr(df0[col],'units',ds[Col].units)
                if hasattr(ds[Col],'long_name'):
                    setattr(df0[col],'long_name',ds[Col].long_name)


            if 'lon' in ds:
                setattr(df0,'longitude',ds['lon'][n].values)
                setattr(df0,'latitude',ds['lat'][n].values)
            self.data.append(df0)




    def _toDataFrame(self):
       #print(self.data)
        return self.data
