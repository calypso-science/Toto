"""Read constituens file
    This import file containing amplitude and phase for each tidal constituents. The function uses the read_csv function from panda <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html>_ to read three columns:
    
    * Constituents name
    * Constituents phase
    * Constituents amplitudes

    This class returns a Panda Dataframe with some extra attributes such as Latitude,Longitude,Units.

    This uses the module Utide. <https://github.com/wesleybowman/UTide>_
    
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
    colNamesLine : int, default 1
        Line number where the header are defined
    unit : str default 'degrees', can be 'radians'
        unit of the phases
    min_date : datetime, default datetime.datetime(2020,1,1)
        Start time of the timeseries 
    max_date : datetime, default datetime.datetime(2020,1,1)
        End time of the timeseries 
    dt : int, default 3600
        Time step in seconds to use when creating the timeserie
    latitude : int, default -40
        Latitude use to calculate the timeserie

    Notes
    -----

    Whe openning the TOTOVIEW gui this function will be called with :py:class:`totoview.inputs.consGUI`

    Examples
    ~~~~~~~~
    
    >>> from toto.inputs.cons import CONSfile
    >>> nc=CONSfile(['cons_list.csv'],sep=',',
                               colNames=[],
                               unit='degrees',
                               miss_val='NaN',
                               colNamesLine=1,
                               skiprows=1,
                               skipfooter=0,
                               col_name={'cons':'Cons','amp':'Amplitude','pha':'Phase'},\
                               )
    >>> nc.reads()
    >>> nc.read_cons() 
    >>> df=nc._toDataFrame()

"""
import glob,os,sys
import pandas as pd
import datetime
import numpy as np
_NUMERIC_KINDS = set('buifc')
from toto.plugins.tide.detide import TideAnalysis
class CONSfile():

    @staticmethod
    def defaultExtensions():
        return ['.csv','.txt']


    def __init__(self,filename,sep='\t',\
                               colNames=[],\
                               unit='degrees',\
                               miss_val='NaN',\
                               colNamesLine=1,\
                               skiprows=1,\
                               skipfooter=0,\
                               col_name={'Cons':'cons','Amplitude':'amp','Phase':'pha'},\
                               min_date=datetime.datetime(2020,1,1),
                               max_date=datetime.datetime(2020,1,9),
                               dt=3600, 
                               latitude=-40,
                               ):

        self.filename     = filename
        self.fileparam=lambda:None

        self.fileparam.sep          = sep
        self.fileparam.colNames     = colNames
        self.fileparam.unit     = unit
        self.fileparam.miss_val     = miss_val
        self.fileparam.ext=self.defaultExtensions()

        self.fileparam.colNamesLine = colNamesLine
        self.fileparam.skiprows     = skiprows
        self.fileparam.skipfooter = skipfooter
        self.fileparam.col_name=col_name

        self.cons=lambda:None
        self.cons.latitude=latitude
        self.cons.min_date=min_date
        self.cons.max_date=max_date
        self.cons.dt=dt
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
               
        try:
            with open(filename,'r',encoding=self.encoding) as f:
                df=pd.read_csv(f,sep=self.fileparam.sep,skiprows=self.fileparam.skiprows,\
                    header=None,names=self.fileparam.colNames,skipfooter=self.fileparam.skipfooter,na_values=self.fileparam.miss_val)
        except pd.errors.ParserError as e:
            raise WrongFormatError('CSV File {}: '.format(filename)+e.args[0])




        self.data.append(df)

    def read_cons(self):

        
        for i,df in enumerate(self.data):
            old_name=self.fileparam.col_name.keys()
            df.rename(columns=self.fileparam.col_name,inplace=True)
            df=df[['Cons','Amplitude','Phase']]
            
            if 'rad' in self.fileparam.unit.lower():
                df['Phase']=df['Phase']*180/np.pi

            df_new=TideAnalysis._cons2ts(self.cons.min_date,self.cons.max_date,self.cons.dt,\
                df['Cons'],df['Amplitude'],df['Phase'],self.cons.latitude)

            df_new.reset_index(inplace=True,drop=False)
            df_new['time']=df_new['index']
            del df_new['index']
            df_new.set_index('time',inplace=True,drop=False)

            self.data[i]=df_new   
            keys=self.data[i].keys()
            for key in keys:
                self.data[i][key].long_name=key  


    def _toDataFrame(self):
        return self.data


if __name__ == '__main__':
    nc=CONSfile(['/home/remy/projects/020_NY/cons_list.csv'],sep=',',\
                               colNames=[],\
                               unit='degrees',\
                               miss_val='NaN',\
                               colNamesLine=1,\
                               skiprows=1,\
                               skipfooter=0,\
                               col_name={'cons':'Cons','amp':'Amplitude','pha':'Phase'},\
                               )
    nc.reads()
    nc.read_cons() 
    df=nc._toDataFrame()



