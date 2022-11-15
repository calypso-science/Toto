"""Read LINZ netcdf file
    This import function works with NetCDF files created from tidal gauge from LINZ.
    It reads both sensors as welll as the README file which should be in the same
    directory.
    This class returns a Panda Dataframe with some extra attributes such as 
    Latitude,Longitude,Units.
    
    Parameters
    ~~~~~~~~~~

    filename : (files,) str or list_like
        A list of filename to process. This can be either a NetCDF file made by linz.downdload
        or a csv file directly downloaded from Linz website

    Examples
    ~~~~~~~~

    >>> from toto.inputs.linz import LINZfile
    >>> nc=LINZfile('filename.nc')._toDataFrame()

"""
import glob,os,sys
import pandas as pd
import xarray as xr
from datetime import datetime, timedelta
import requests
from multiprocessing.pool import ThreadPool

def url_response(url):

    fileout, url = url
    linzfile = requests.get(url, allow_redirects=True)
    if linzfile.status_code != 404:
        with open(fileout, 'wb') as fd:
            for chunk in linzfile.iter_content(chunk_size=128):
                fd.write(chunk)

def lat2msl(readme, ds,sensor=41):
    # Converts data to mean sea level based on information contained in the station's readme
    print(f'Reading data from sensor {sensor}')
    f = open(readme,
             encoding='latin-1')
    readme = f.readlines()
    reference_mark=False
    for il,line in enumerate(readme):
        if 'WGS-84 POSITION' in line:
            line = line.replace('Â','').replace('°','').replace("'",'').replace("\"",'')

            if 'S' in line:
                line = line.replace("S",'').split(' ')
                fac = -1
            else:
                fac = 1
                line = line.replace("N",'').split(' ')

            lat_deg = float(line[4])
            lat_dec = float(line[5])
            lat_sec = float(line[6]) if len(line) >=7 else 0
            lat = (lat_deg + lat_dec/60 + lat_sec/3600)*fac

            line = readme[il+1]
            line = line.replace('Â','').replace('°','').replace("'",'').replace("\"",'')
            if 'W' in line:
                line = line.replace("W",'').strip().split(' ')
                fac = -1
            else:
                fac = 1
                line = line.replace("E",'').strip().split(' ')

            lon_deg = float(line[0])
            lon_dec = float(line[1])
            lon_sec = float(line[2]) if len(line) >=3 else 0
            lon = (lon_deg + lon_dec/60 + lon_sec/3600)*fac

        if 'GAUGE ZERO' in line:
            reference_mark = line.split(' ')[6]

    if not reference_mark:
        print('Line GAUGE ZERO not found')
        return ds,lon,lat


    for line in readme:
        if 'LINZ geodetic code' in line and reference_mark in line:
            try:
                ref_datum = float(line.split(',')[-1].split()[0])
            except:
                # print('Reference bench mark not found. Will set to time average water level after correcting height drifting')
                # ref_datum = 0
                ref_datum = 3.4878
                print(f'Hardcoding reference bench mark = {ref_datum}')
                # req = requests.get("https://www.geodesy.linz.govt.nz/gdb/index.cgi?code=DD1N")
                # text = req.text
                # for i, line in enumerate(text.split('\n')):
                #     if 'Vertical Datum' in line:
                #         print(f'{i}   {line}')



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
    count, key_idx = 1, 1
    line = readme[start + count]
    while line != '\r\n' and line != '\n':
        m1 = datetime.strptime(line.split(' ')[0], '%b').month
        y1 = int(line.split(' ')[1])
        try:
            m2 = datetime.strptime(line.split(' ')[3], '%b').month + 1
            y2 = int(line.split(' ')[4][:-1])
            if m2 > 12:
                m2 = 1
                y2 += 1
            d2, H2, M2, S2 = 1, 0, 0, 0
        except:
            if line.split(' ')[2] == '->':
                y2, m2, d2, H2, M2, S2 = ds.index[-1].year, ds.index[-1].month, ds.index[-1].day,\
                    ds.index[-1].hour, ds.index[-1].minute, ds.index[-1].second

        key = 'ref{}'.format(key_idx)
        try:
            ref = float(line.split(' ')[5]) - ref_datum
            ref_gauge[key] = dict()
            ref_gauge[key]['value'] = ref
            ref_gauge[key]['t1'] = datetime(y1, m1, 1)
            ref_gauge[key]['t2'] = datetime(y2, m2, d2, H2, M2, S2)
            key_idx += 1
        except:
            print(f"Skipping {line}")

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

    if ref_datum == 0:
        ref_datum = ds.mean()
        ds = ds - ref_datum
        print(f'Assuming reference datum equal to time average of water levels = {ref_datum:.2f}')

    return ds,lon,lat
def download_linz(station,start_date,end_date=None,fileout=None,sensors=[40,41]):
    #https://sealevel-data.linz.govt.nz/AUCT/2019/40/AUCT_40_2019001.zip
    #https://sealevel-data.linz.govt.nz/AUCT/2014/40/AUCT_40_2014.zip
    baseurl='https://sealevel-data.linz.govt.nz/%s/%i/%i/%s_%i_%s.zip'
    if not end_date:
        end_date=datetime.now()

    if type(sensors)!=type(list()):
        sensors=[sensors]



    for sensor in sensors:
        urls=[]
        for y in range(start_date.year,end_date.year+1):
            for n in range(1,367):
                fileout=os.path.join(os.getcwd(),'linz_'+str(sensor)+'_'+str(y)+'%03i.zip'%n)
                urls=(fileout,
                    baseurl % (station,y,sensor,station,sensor,str(y)+'%03i'%n))

                url_response(urls)
#        ThreadPool(1).imap_unordered(url_response, urls)


class LINZfile():

    @staticmethod
    def defaultExtensions():
        return ['.nc']


    def __init__(self,filenames):

        if isinstance(filenames,str):
            filenames=[filenames]
        self.filenames=filenames
        self.data=[]

        self._reads()

    def _reads(self):
        for file in self.filenames:
            if file.endswith('.csv'):
                self._read_csv(file)
            elif file.endswith('.nc'):
                self._read_nc(file)

    def _read_csv(self,filename):
        sensor=filename.split('_')[-2]
        station=filename.split('_')[-3]
        df=pd.read_csv(filename,delimiter=',',
            names=['station','date_time','elev'+sensor],
            parse_dates=['date_time'])

        df.rename(columns={'date_time':'time'},inplace=True)
        del df['station']

        
        filepath,filename=os.path.split(filename)
        readmefile=os.path.join(filepath,station+'_readme.txt')
        df.set_index('time',inplace=True)
        df['elev'+sensor],lon,lat=lat2msl(readmefile, df['elev'+sensor],sensor=int(sensor))
        df.reset_index(inplace=True)
        df.set_index('time',inplace=True,drop=False)


        setattr(df['elev'+sensor],'units','m')
        setattr(df['elev'+sensor],'long_name','water_level')


        setattr(df,'longitude',lon)
        setattr(df,'latitude',lat)           
        self.data.append(df)


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
            df = df.assign(longitude=ds['longitude'].values[0])
            df = df.assign(latitude=ds['latitude'].values[0])
        else:
            df = df.assign(longitude=lon)
            df = df.assign(latitude=lat)
        self.data.append(df)



    def _toDataFrame(self):
       #print(self.data)
        return self.data


if __name__ == '__main__':
    #LINZfile('/home/remy/projects/019_stormsurge/storm_surge_data/nz_tidal_gauges/linz/raw/AUCT_raw.nc')
    download_linz('AUCT',datetime(2010,1,1),end_date=None,fileout=None,sensors=[40,41])