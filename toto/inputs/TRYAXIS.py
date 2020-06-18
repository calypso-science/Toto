"""Read TRYAXIS files.
"""
import glob,os,sys
import pandas as pd
import datetime as dt
import numpy as np

class TRYAXISfile():

    @staticmethod
    def defaultExtensions():
        return ['.NONDIRSPEC','.DIRSPEC']


    def __init__(self,filenames):

        if isinstance(filenames,str):
            filenames=[filenames]

        self.filenames=filenames

        self.data=[]

        # READ NONIRCSPCE
        if self.filenames[0].endswith('NONDIRSPEC'):
            self._reads_NONDIRSPEC()



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


