"""Read MATLAB file
    This import mat file. This class returns a Panda Dataframe with some extra attributes such as Latitude,Longitude,Units.
    
    Parameters
    ~~~~~~~~~~

    filename : (files,) str or list_like
        A list of filename to process.

    Notes
    -----

    The file MUST contain a variable called `time`, `t` or `timestamp` with matlab datenum time steps

    Examples
    ~~~~~~~~

    >>> from toto.inputs.mat import MATfile
    >>> nc=MATfile('filename.mat')._toDataFrame()
"""
import glob,os,sys
import pandas as pd

from scipy.io import loadmat
import numpy as np
import datetime as dt

TIMES=['t','time','timestamp']

def matlab2datetime(matlab_datenum):
    day = dt.datetime.fromordinal(int(matlab_datenum))
    dayfrac = dt.timedelta(days=matlab_datenum%1) - dt.timedelta(days = 366)
    return day + dayfrac

class MATfile():

    @staticmethod
    def defaultExtensions():
        return ['.mat']


    def __init__(self,filenames):
        if isinstance(filenames,str):
            filenames=[filenames]


        self.filenames=filenames

        self.data=[]

        # READ 
        self._reads_mat()

    def _reads_mat(self):
        for file in self.filenames:
            self._read_mat(file)


    def _read_mat(self,filename):
       
        mat = loadmat(filename)  # load mat-file
        columns=[key for key in mat.keys() if not key.startswith('_')]
        columns_lower=[col.lower() for col in columns]
        df = pd.DataFrame(np.vstack([mat[c].flatten() for c in columns]).T,columns=columns)
        time_col_name=False
        for time_name in TIMES:
            if time_name in columns_lower:
                time_col_name=columns[columns_lower.index(time_name)]
                continue

        if not time_col_name:
            print('Time variable could not be found')
            sys.exit(-1)

        df.rename(columns={time_col_name:'time'},inplace=True)

        time=[matlab2datetime(tval) for tval in df['time']]
        df['time']=time
        df.set_index('time',inplace=True,drop=False)

        self.data.append(df)

    def _toDataFrame(self):
        return self.data


if __name__ == '__main__':
    MATfile('../../../test/test.mat')