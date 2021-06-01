"""Read TRYAXIS files.
Only reads:
   - *.NONDIRSPEC
   - *.DIRSPEC
"""
import glob,os,sys
import pandas as pd
import datetime as dt
import numpy as np

class TRYAXISfile():

    @staticmethod
    def defaultExtensions():
        return ['.NONDIRSPEC','.WAVE']


    def __init__(self,filenames):

        if isinstance(filenames,str):
            filenames=[filenames]

        self.filenames=filenames

        self.data=[]

        # READ NONIRCSPCE
        if self.filenames[0].endswith('NONDIRSPEC'):
            self._reads_NONDIRSPEC()

        # READ NONIRCSPCE
        if self.filenames[0].endswith('WAVE'):
            self._reads_WAVE()

    def _read_WAVE(filename):
        # Using readline()
        wave={}
        file1 = open(filename, 'r')
        count = 0
         
        while True:
            count += 1
            # Get next line from file
            line = file1.readline()
            # if line is empty
            # end of file is reached
            if not line:
                break

            if count>3:
                name,value=line.split('=')
                if count==4:
                    value=pd.to_datetime(value.rstrip(), format=' %Y-%m-%d %H:%M(UTC)')
                elif count>7:
                    try:
                        value=float(value)
                    except:
                        value=np.nan
                else:
                    value=value.rstrip()
                wave[name.rstrip().replace(' ','_')]=value

        file1.close()
        return wave
    def _reads_WAVE(self):
        ds=[]
        for i,file in enumerate(self.filenames):
            ds.append(TRYAXISfile._read_WAVE(file))

        keys=[]
        for d in ds:
            keys+=d.keys()
        keys=list(set(keys))

        di = {}
        for key in keys:
            di[key]=[]
            for d in ds:
                if key in d:
                    di[key].append(d[key])
                else:
                    di[key].append(np.nan)


        df=pd.DataFrame.from_dict(di,orient='columns')
        df=df.rename(columns={'DATE':'time'})
        df.set_index('time',inplace=True,drop=False)
        df.sort_index(inplace=True)
        self.data.append(df)
    def _reads_NONDIRSPEC(self):
        for file in self.filenames:
            self._read_NONDIRSPEC(file)



    def _read_NONDIRSPEC(self,filename):
       
        try:
            with open(filename,'r',encoding=None) as f:
                df=pd.read_csv(f,sep='  ',skiprows=9,names=['freq','density'],engine='python')
        except pd.errors.ParserError as e:
            raise WrongFormatError('TryAxis File {}: '.format(filename)+e.args[0])


        def readline(iLine):
            with open(filename,'r',encoding=None) as f:
                for i, line in enumerate(f):
                    if i==iLine:
                        return line.strip()
                    elif i>iLine:
                        break



        time=pd.to_datetime(readline(3), format='DATE    = %Y %b %d %H:%M(UTC)')
        df.set_index('freq',inplace=True,drop=False)
        time=np.repeat(time,len(df.index), axis = 0)
        df['time']=time

        self.data.append(df)


    def _toDataFrame(self):
       #print(self.data)
        return self.data


