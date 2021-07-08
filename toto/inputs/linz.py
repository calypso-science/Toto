"""Read generic netcdf file

"""
import glob,os,sys
import pandas as pd
import xarray as xr
from datetime import datetime, timedelta

def lat2msl(readme, ds,sensor=41):
    # Converts data to mean sea level based on information contained in the station's readme
    f = open(readme,
             encoding='latin-1')
    readme = f.readlines()
    reference_mark=False
    for il,line in enumerate(readme):
        if 'WGS-84 POSITION' in line:
            line=line.replace('Â','').replace('°','').replace("'",'')

            if 'S' in line:
                line=line.replace("S",'')
                fac=-1
            else:
                fac=1
                line=line.replace("N",'')

            lat_deg=float(line.split(' ')[4])
            lat_dec=float(line.split(' ')[5])
            lat=(lat_deg+lat_dec/60)*fac

            line=readme[il+1]
            line=line.replace('Â','').replace('°','').replace("'",'')
            if 'W' in line:
                line=line.replace("W",'')
                fac=-1
            else:
                fac=1
                line=line.replace("E",'')

            lon_deg=float(line.split(' ')[-2])
            lon_dec=float(line.split(' ')[-1])
            lon=(lon_deg+lon_dec/60)*fac

        if 'SUMMARY OF TIDE GAUGE ZERO' in line:
            reference_mark = line.split(' ')[6]

    if not reference_mark:
        print('Line SUMMARY OF TIDE GAUGE ZERO not found')
        return ds,lon,lat


    for line in readme:
        if 'LINZ geodetic code' in line and reference_mark in line:
            try:
                ref_datum = float(line.split(',')[-1].split()[0])
            except:
                print('reference bench mark not found set to 0')
                ref_datum=0


    start=False
    if sensor==41:
        for idx, line in enumerate(readme):
            if 'SENSOR 41' in line:
                start = idx
                break
    elif sensor ==40:
        for idx, line in enumerate(readme):
            if 'SENSOR 40' in line:
                start = idx
                break


    if not start:
        print('No information for sensor # %i' % sensor)
        return ds,lon,lat


    line = 'start'
    ref_gauge = dict()
    count = 1
    line = readme[start + count]
    while line != '\r\n' and line != '\n':
        m1 = datetime.strptime(line.split(' ')[0], '%b').month
        y1 = int(line.split(' ')[1])
        m2 = datetime.strptime(line.split(' ')[3], '%b').month + 1
        y2 = int(line.split(' ')[4][:-1])
        if m2 > 12:
            m2 = 1
            y2 += 1

        key = 'ref{}'.format(count)
        ref_gauge[key] = dict()
        ref_gauge[key]['value'] = float(line.split(' ')[5]) - ref_datum
        ref_gauge[key]['t1'] = datetime(y1, m1, 1)
        ref_gauge[key]['t2'] = datetime(y2, m2, 1)
        count += 1
        line = readme[start + count]


    for c in range(len(ref_gauge)):
        key = 'ref{}'.format(c+1)
        if key == 'ref1': # start
            if ds.index[0] < ref_gauge['ref1']['t1']:
                ref_gauge['ref1']['t1'] = ds.index[0]

            if c != len(ref_gauge) - 1:
                if ref_gauge['ref{}'.format(c+2)]['t1'] - ref_gauge[key]['t2'] > timedelta(days=1) and len(ref_gauge) > 1:
                    ref_gauge[key]['t2'] = ref_gauge['ref{}'.format(c+2)]['t1'] - timedelta(hours=1)

        elif c == len(ref_gauge) - 1: # end
            if ref_gauge[key]['t2'] < ds.index[-1]:
                ref_gauge[key]['t2'] = ds.index[-1]

        else: # middle
            if ref_gauge['ref{}'.format(c+2)]['t1'] - ref_gauge[key]['t2'] > timedelta(days=1):
                ref_gauge[key]['t2'] = ref_gauge['ref{}'.format(c+2)]['t1'] - timedelta(hours=1)

        ds[ref_gauge[key]['t1'] : ref_gauge[key]['t2']] = ds[ref_gauge[key]['t1'] : ref_gauge[key]['t2']] - ref_gauge[key]['value']

    return ds,lon,lat

class LINZfile():

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
        if 'site' in ds:
            ds=ds.sel({'site':0})

        if 'sensor' in ds:
            if len(ds['sensor'])>1:              
                df=ds.sel({'sensor':40})['elev'].to_dataframe()
                del df['sensor']
                df.rename(columns={'elev':'elev40'},inplace=True)
                df41=ds.sel({'sensor':41})['elev'].to_dataframe()
                df['elev41']=df41['elev'].copy()
                del df41
            else:
                df=ds['elev'][0].to_dataframe()
                del df['sensor']
                df.rename(columns={'elev':'elev40'},inplace=True)
        else:
            df=ds['elev'].to_dataframe()
            df.rename(columns={'elev':'elev40'},inplace=True)

        filepath,filename=os.path.split(filename)
        readmefile=os.path.join(filepath,filename.replace('_raw.nc','_readme.txt'))

        if not os.path.isfile(readmefile):
            print('Readme file %s could not be found' % readmefile)
            sys.exit(-1)

        if 'elev41' in df:
            df['elev41'],lon,lat=lat2msl(readmefile, df['elev41'],sensor=41)
        if 'elev40' in df:
            df['elev40'],lon,lat=lat2msl(readmefile, df['elev40'],sensor=40)

        df.reset_index(inplace=True)
        df.set_index('time',inplace=True,drop=False)
        if 'elev40' in df:
            setattr(df['elev40'],'units','m')
            setattr(df['elev40'],'long_name','water_level')
        if 'elev41' in df:
            setattr(df['elev41'],'units','m')
            setattr(df['elev41'],'long_name','water_level')

        if 'longitude' in ds:
            setattr(df,'longitude',ds['longitude'].values)
            setattr(df,'latitude',ds['latitude'].values)
        else:
            setattr(df,'longitude',lon)
            setattr(df,'latitude',lat)           
        self.data.append(df)




    def _toDataFrame(self):
       #print(self.data)
        return self.data


if __name__ == '__main__':
    LINZfile('/home/remy/projects/019_stormsurge/storm_surge_data/nz_tidal_gauges/linz/raw/AUCT_raw.nc')