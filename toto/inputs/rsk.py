"""Read RSK file from RBR Ltd
    This import raw file for a RBR pressure sensor.
    This class returns a Panda Dataframe.
    
    Parameters
    ~~~~~~~~~~

    filename : (files,) str or list_like
        A list of filename to process.


    Examples
    ~~~~~~~~

    >>> from toto.inputs.rsk import RSKfile
    >>> nc=RSKfile('filename.rsk')._toDataFrame()
"""



import glob,os,sys
import pandas as pd
import datetime 
import numpy as np
import sqlite3

class RSKfile():

    @staticmethod
    def defaultExtensions():
        return ['.rsk']


    def __init__(self,filenames):

        if isinstance(filenames,str):
            filenames=[filenames]

        self.filenames=filenames

        self.data=[]

        self._reads_rsk()

    def _reads_rsk(self):
        for file in self.filenames:
            self._read_rsk(file)

    def _read_rsk(self,filename):
        df0 = pd.DataFrame()
        raw = sqlite3.connect('file:%s?mode=ro' % filename, uri=True)
        #try:
        Start_time=raw.execute('select * from Data ORDER BY ROWID ASC LIMIT 1').fetchall()
        schedules=raw.execute('select samplingPeriod from continuous').fetchall()
        sampleSize=raw.execute('select sampleSize from deployments').fetchall()
        ## Header file
        serial=raw.execute('select serialID from instruments').fetchall()
        # compute the time
        Tstart=datetime.datetime.fromtimestamp(Start_time[0][1]/1000)
        dt=schedules[0][0]
        df0['time']=pd.date_range(Tstart.strftime('%Y/%m/%d %H:%M:%S'),
                           periods=sampleSize[0][0], freq='%ims'%dt)
        
        
        df0.set_index('time',inplace=True,drop=False)
        channels=raw.execute("""select channelID,
                              shortName,
                              longName,
                              units,
                              isDerived
                         from channels
                     order by channelId asc""").fetchall()

        #[(1, 'cond05', 'Conductivity', 'mS/cm', 0), (2, 'temp03', 'Temperature', '°C', 0), (3, 'pres07', 'Pressure', 'dbar', 0), (4, 'doxy06', 'Dissolved O₂', '%', 0), (5, 'turb00', 'Turbidity', 'NTU', 0), (6, 'par_01', 'PAR', 'µMol/m²/s', 0), (7, 'fluo01', 'Chlorophyll', 'µg/l', 0), (8, 'pres08', 'Sea pressure', 'dbar', 1), (9, 'dpth01', 'Depth', 'm', 1), (10, 'sal_00', 'Salinity', 'PSU', 1)]
        data=raw.execute('select * from Data')
        #.fetchall()
        description=data.description
        name=[x[0] for x in description]

        data=data.fetchall()
        matrix=np.array([x[1:] for x in data])

        idx=np.argsort(matrix[:,0])
        matrix=matrix[idx,:]
        for channel in channels:
            if 'channel0%i'%channel[0] in name:
                idx=name.index('channel0%i'%channel[0])
                df0[channel[2]]=matrix[:,channel[0]]
                setattr(df0[channel[2]],'units',channel[3])
                setattr(df0[channel[2]],'long_name',channel[2])
        

        if 'Pressure' in df0:
            df0['Sealevel']=(df0['Pressure']-10.1325)*1.019716
            setattr(df0['Sealevel'],'units','m')
            setattr(df0['Sealevel'],'long_name','Sea level')
        

        
        self.data.append(df0)




    def _toDataFrame(self):
       #print(self.data)
        return self.data


if __name__ == '__main__':

    nc=RSKfile('../../_tests/rsk/sample.rsk')._toDataFrame()
    print(nc)