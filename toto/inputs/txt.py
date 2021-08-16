"""Read txt,csv file
    This import text file. The function uses the read_csv function from panda <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html>_.
    This class returns a Panda Dataframe with some extra attributes such as Latitude,Longitude,Units.
    
    Parameters
    ~~~~~~~~~~

    filename : (files,) str or list_like
        A list of filename to process.
    sep : str, default {_default_sep}
        Delimiter to use. If sep is None, the C engine cannot automatically detect
        the separator, but the Python parsing engine can, meaning the latter will
        be used and automatically detect the separator by Python's builtin sniffer
        tool, ``csv.Sniffer``. In addition, separators longer than 1 character and
        different from ``'\s+'`` will be interpreted as regular expressions and
        will also force the use of the Python parsing engine. Note that regex
        delimiters are prone to ignoring quoted data. Regex example: ``'\r\t'``.
    skiprows : list-like, int or callable, optional
        Line numbers to skip (0-indexed) or number of lines to skip (int)
        at the start of the file.
        If callable, the callable function will be evaluated against the row
        indices, returning True if the row should be skipped and False otherwise.
        An example of a valid callable argument would be ``lambda x: x in [0, 2]``.
    skipfooter : int, default 0
        Number of lines at bottom of file to skip (Unsupported with engine='c').
    miss_val : scalar, str, list-like, or dict, optional
        Additional strings to recognize as NA/NaN. If dict passed, specific
        per-column NA values.  
    colNamesLine : int, default 1
        Line number where the header are defined
    unitNamesLine : int, default 1
        Line number where the units are defined        
    single_column : bool, default False
        The time is represented in a single column
    customUnit : str, default '%d-%m-%Y %H:%M:%S'
        String reprensenting the time format
    unit : str default 's', can be 'auto','custom','matlab' or 's' and 'D'
        unit of the single column time. Only matter if `single_column` is True
    time_col_name: dict, default {'Year':'year','Month':'month','Day':'day','Hour':'hour','Min':'Minute','Sec':'Second'}
        Dictonary for renaming the each column, so Panda can interprate the time. Only matter if `single_column` is False
    colNames : List, default []
        List of column names to use.
    unitNames : List, default []
        List of unit to use. 

    Notes
    -----

    Whe openning the TOTOVIEW gui this function will be called with :py:class:`totoview.inputs.txtGUI`

    Examples
    ~~~~~~~~

    >>> from toto.inputs.txt import TXTfile 
    >>> tx=TXTfile([filename],colNamesLine=1,miss_val='NaN',\
    sep=',',skiprows=1,unit='custom',time_col_name='time',unitNamesLine=0,\
    single_column=True,customUnit='%d/%m/%Y %H:%M')
    >>> tx.reads()
    >>> tx.read_time()
    >>> df=tx._toDataFrame()
"""

import glob,os,sys
import pandas as pd
import datetime as dt
import numpy as np
_NUMERIC_KINDS = set('buifc')

def matlab2datetime(matlab_datenum):
    day = dt.datetime.fromordinal(int(matlab_datenum))
    dayfrac = dt.timedelta(days=matlab_datenum%1) - dt.timedelta(days = 366)
    return day + dayfrac



class TXTfile():

    @staticmethod
    def defaultExtensions():
        return ['.csv','.txt']


    def __init__(self,filename,sep='\t',\
                               colNames=[],\
                               unitNames=[],\
                               miss_val='NaN',\
                               colNamesLine=1,\
                               skiprows=2,\
                               unitNamesLine=2,\
                               skipfooter=0,\
                               single_column=False,\
                               unit='s',\
                               customUnit='%d-%m-%Y %H:%M:%S',\
                               time_col_name={'Year':'year','Month':'month','Day':'day','Hour':'hour','Min':'Minute','Sec':'Second'},\
                               ):
        self.filename     = filename
        self.fileparam=lambda:None

        self.fileparam.sep          = sep
        self.fileparam.colNames     = colNames
        self.fileparam.unitNames     = unitNames
        self.fileparam.miss_val     = miss_val
        self.fileparam.ext=self.defaultExtensions()

        self.fileparam.colNamesLine = colNamesLine
        self.fileparam.skiprows     = skiprows
        self.fileparam.unitNamesLine = unitNamesLine
        self.fileparam.skipfooter = skipfooter

        self.fileparam.single_column=single_column
        self.fileparam.unit=unit
        self.fileparam.customUnit=customUnit


        self.fileparam.time_col_name=time_col_name

        self.encoding    = None

        self.data=[]

        # set usr defined parameter

    def reads(self):
        for file in self.filename:
            self.read(file)

    def read(self,filename):

        # --- Detecting encoding
        # NOTE: done by parent class method
        
        # --- Subfunctions
        def readline(iLine):
            with open(filename,'r',encoding=self.encoding) as f:
                for i, line in enumerate(f):
                    if i==iLine:
                        return line.strip()
                    elif i>iLine:
                        break
        def split(s):
            if s is None:
                return []
            if self.fileparam.sep=='\s+':
                return s.strip().split()
            else:
                return s.strip().split(self.fileparam.sep)
        def strIsFloat(s):
            try:
                float(s)
                return True
            except:
                return False
        # --- Safety
        if self.fileparam.sep=='' or self.fileparam.sep==' ':
            self.fileparam.sep='\s+'

        iStartLine=0

        # Column header
        line=readline(max(0,self.fileparam.colNamesLine-1))
        self.fileparam.colNames=split(str(line).strip())
        
        # unit header
        if self.fileparam.unitNamesLine:
            line=readline(max(0,self.fileparam.unitNamesLine-1))
            unit={}
            unitNames=split(str(line).strip())
            for i,col in enumerate(self.fileparam.colNames): 
                unit[col]=unitNames[i].replace('[','').replace(']','')

            self.fileparam.unitNames=unit

        
        try:
            with open(filename,'r',encoding=self.encoding) as f:
                df=pd.read_csv(f,sep=self.fileparam.sep,skiprows=self.fileparam.skiprows,\
                    header=None,names=self.fileparam.colNames,skipfooter=self.fileparam.skipfooter,na_values=self.fileparam.miss_val)
        except pd.errors.ParserError as e:
            raise WrongFormatError('CSV File {}: '.format(filename)+e.args[0])




        self.data.append(df)

    def read_time(self):

        

        for i,df in enumerate(self.data):

            if self.fileparam.single_column is True:
                if self.fileparam.unit == 'auto':
                    time=pd.to_datetime(df[self.fileparam.time_col_name])
                elif self.fileparam.unit == 'matlab':
                    time=[matlab2datetime(tval) for tval in df['time']]
                elif self.fileparam.unit == 's' or self.fileparam.unit == 'D':
                    time=pd.to_datetime(df[self.fileparam.time_col_name],unit=self.fileparam.unit)
                elif self.fileparam.unit == 'custom':
                    time=pd.to_datetime(df[self.fileparam.time_col_name],format=self.fileparam.customUnit)
                del df[self.fileparam.time_col_name]
            else:
                old_name=self.fileparam.time_col_name.keys()


                time=pd.to_datetime(df[old_name].rename(columns=self.fileparam.time_col_name))

                for oldkey in old_name:
                    del df[oldkey]



            self.data[i]=df
            self.data[i]['time']=time
            self.data[i].set_index('time',inplace=True,drop=False)
            

            self.add_unit(i)
            keys=self.data[i].keys()
            for key in keys:
                self.data[i][key].long_name=key  



            # keys=list(df.keys())
            # for key in keys:
            #     if np.all(df[key].isna()):
            #         del df[key] 

            #     ### check if all numerics
            #     if not np.asarray(df[key].values).dtype.kind in _NUMERIC_KINDS:
            #         print('Warning %s: this key was deleted containes string' % key)
            #         del df[key]

    def add_unit(self,i):

        keys=self.data[i].keys()
        for key in keys:
            if key in self.fileparam.unitNames:
                units=self.fileparam.unitNames[key]
                self.data[i][key].units=units

            elif '[' in key and ']' in key:
                a,b=key.split('[')
                self.data[i].rename(columns={key: a},inplace=True)
                self.data[i][a].units=b.split(']')[0]



    def _toDataFrame(self):
        return self.data
