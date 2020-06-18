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
        self.unit=[]

        # READ 
        self._reads_nc()



    def _reads_nc(self):
        for file in self.filenames:
            self._read_nc(file)



    def _read_nc(self,filename):
       

        ds = xr.open_dataset(filename)
        df = ds.to_dataframe()

        nsite=df.index.max()[1]
        for n in range(0,nsite+1):
            df0=df.loc[(0,n)]
            df0.reset_index(inplace=True)
            df0.set_index('time',inplace=True,drop=False)

            for col in list(df0.columns):
                if hasattr(ds[col],'units'):
                    setattr(df0[col],'units',ds[col].units)
                if hasattr(ds[col],'long_name'):
                    setattr(df0[col],'long_name',ds[col].long_name)

            self.data.append(df0)



    def _toDataFrame(self):
       #print(self.data)
        return self.data
