"""Read generic netcdf file
    This import function works well is NetCDF or Zarr files created by `XARRAY`.
    This class returns a Panda Dataframe with some extra attributes such as Latitude,Longitude,Units.
    
    Parameters
    ~~~~~~~~~~

    filename : (files,) str or list_like
        A list of filename to process.

    Examples
    ~~~~~~~~

    >>> from toto.inputs.nc import NCfile
    >>> nc=NCfile('filename.nc')._toDataFrame()
"""
import glob,os,sys
import pandas as pd
import xarray as xr


class NCfile():

    @staticmethod
    def defaultExtensions():
        return ['.nc','.zarr']


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
        if '.zarr' in filename:
            ds = xr.open_zarr(filename)
        else:
            ds = xr.open_dataset(filename)

        df=ds.to_dataframe()

        if len(df.index.names)==1:
            if 'lon' in ds:
                setattr(df,'longitude',ds['lon'].values)
                setattr(df,'latitude',ds['lat'].values)
            if 'longitude' in ds:
                setattr(df,'longitude',ds['longitude'].values)
                setattr(df,'latitude',ds['latitude'].values)

            self.data.append(df)

        else:
            sub_index=list(df.index.names)
            if 'time' in sub_index:
                del sub_index[sub_index.index('time')]


            sub_index1=df.index.get_level_values(sub_index[0]).unique()
            for nsub in sub_index1:
                df1=df.iloc[df.index.get_level_values(sub_index[0]) == nsub].reset_index(sub_index[0])
                del df1[sub_index[0]]
                df1=df1.add_suffix('_'+sub_index[0]+str(nsub))


                if len(sub_index)>1:
                    sub_index2=df.index.get_level_values(sub_index[1]).unique()
                    for nsub2 in sub_index2:
                        df2=df1.iloc[df1.index.get_level_values(sub_index[1]) == nsub2].reset_index(sub_index[1])
                        del df2[sub_index[1]]
                        df2=df2.add_suffix('_'+sub_index[1]+str(nsub2))
                        

                    if len(sub_index)>2:
                        sub_index3=df.index.get_level_values(sub_index[2]).unique()
                        for nsub3 in sub_index3:
                            df3=df2.iloc[df2.index.get_level_values(sub_index[2]) == nsub3].reset_index(sub_index[2])
                            del df3[sub_index[2]]
                            df3=df3.add_suffix('_'+sub_index[2]+str(nsub3))

                            if len(sub_index)>3:
                                sub_index4=df.index.get_level_values(sub_index[3]).unique()
                                for nsub4 in sub_index4:
                                    df4=df3.iloc[df3.index.get_level_values(sub_index[3]) == nsub4].reset_index(sub_index[3])
                                    del df4[sub_index[3]]
                                    df4=df4.add_suffix('_'+sub_index[3]+str(nsub4))
                                    df4.reset_index(inplace=True)
                                    df4.set_index('time',inplace=True,drop=False)
                                    self.data.append(df4)
                            else:
                                df3.reset_index(inplace=True)
                                df3.set_index('time',inplace=True,drop=False)
                                self.data.append(df3) 
                    else:
                        df2.reset_index(inplace=True)
                        df2.set_index('time',inplace=True,drop=False)
                        self.data.append(df2)


                else:
                    df1.reset_index(inplace=True)
                    df1.set_index('time',inplace=True,drop=False)
                    self.data.append(df1)


                #import pdb;pdb.set_trace()



        # D1_keys=[]
        # D2_keys=[]
        # key_to_drop=[]
        # for key in ds.keys():
        #     if 'time' in ds[key].dims:
        #         if 'lev' in ds[key].dims:
        #             D2_keys.append(key)
        #         else:
        #             D1_keys.append(key)

        #     else:
        #         key_to_drop.append(key)

        # ds.drop_vars(key_to_drop)

        # df = ds.to_dataframe()


        # df0=[]
        # if len(D2_keys)>0:
        #     nlev=df.index.get_level_values('lev').unique()
        #     for m in nlev:
        #         df2d=df[D2_keys].loc[(m)]
        #         df2d.reset_index(inplace=True)
        #         df2d.set_index('time',inplace=True)
        #         df2d=df2d.add_suffix('_lev_'+str(m))
        #         df0.append(df2d)
              
        # if len(D1_keys)>0:
        #         df1d=df[D1_keys]
        #         df1d.reset_index(inplace=True)
        #         df1d.set_index('time',inplace=True)
        #         df0.append(df1d)

        # df0=pd.concat(df0,axis=1)
        # df0.reset_index(inplace=True)
        # df0.set_index('time',inplace=True,drop=False)
        # for col in list(df0.columns):
        #     if '_lev_' in col:
        #         Col=col.split('_lev_')[0]
        #     else:
        #         Col=col
        #     if hasattr(ds[Col],'units'):
        #         setattr(df0[col],'units',ds[Col].units)
        #     if hasattr(ds[Col],'long_name'):
        #         setattr(df0[col],'long_name',ds[Col].long_name)


        # if 'lon' in ds:
        #     setattr(df0,'longitude',ds['lon'].values)
        #     setattr(df0,'latitude',ds['lat'].values)
        # self.data.append(df0)




    def _toDataFrame(self):
       #print(self.data)
        return self.data

if __name__ == '__main__':
    ncfile='/home/remy/projects/ms/tidal_points/tidal_prediction.nc'
    ncfile='/home/remy/developpement/sst/OISST.nc'
    nc=NCfile(ncfile)
    df=nc._toDataFrame()