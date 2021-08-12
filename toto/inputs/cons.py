"""Read generic txt files.
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



