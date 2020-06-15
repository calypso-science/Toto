"""Read generic txt files.
Functions:
    read_generic: Read Spectra from SWAN ASCII file
    read_generics: Read multiple swan files into single Dataset
"""
import glob,os,sys
import pandas as pd
import datetime as dt
from .__txtGUI import ImportGUI,parse_time_GUI

def xstr(s):
    if s is None:
        return ''
    return str(s)
def strx(s):
    if s is '':
        return None

    return int(s)
def matlab2datetime(matlab_datenum):
    day = dt.datetime.fromordinal(int(matlab_datenum))
    dayfrac = dt.timedelta(days=matlab_datenum%1) - dt.timedelta(days = 366)
    return day + dayfrac

def center_window(window):
    frameGm = window.frameGeometry()
    screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
    centerPoint = QApplication.desktop().screenGeometry(screen).center()
    frameGm.moveCenter(centerPoint)
    window.move(frameGm.topLeft())



class TXTfile():

    @staticmethod
    def defaultExtensions():
        return ['.csv','.txt']


    def __init__(self,parent):
        #self.filename     = filename
        self.fileparam=lambda:None

        self.parent   =parent
        self.fileparam.sep          = '\t'
        self.fileparam.colNames     = []
        self.fileparam.unitNames     = []
        self.fileparam.miss_val     = 'NaN'
        self.fileparam.ext=self.defaultExtensions()

        self.fileparam.colNamesLine = 1
        self.fileparam.skiprows     = 2
        self.fileparam.unitNamesLine = 2
        self.fileparam.skipfooter = 0

        self.fileparam.single_column=True
        self.fileparam.unit='s'
        self.fileparam.customUnit='%d-%m-%Y %H:%M:%S'


        self.fileparam.time_col_name=[]

        self.encoding    = None





        self.data={}
        # set usr defined parameter
        tmp=ImportGUI(self.fileparam,self.parent)
        self.fileparam=tmp.TXTfile
        self._reads()
        # # Parse the date
        tmp=parse_time_GUI(self.fileparam,self.parent)
        self.fileparam=tmp.TXTfile
        self._read_time()


    def _reads(self):
        for file in self.fileparam.filename:
            self._read(file)



    def _read(self,filename):

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
            self.fileparam.unitNames=split(str(line).strip())

        
        try:
            with open(filename,'r',encoding=self.encoding) as f:
                df=pd.read_csv(f,sep=self.fileparam.sep,skiprows=self.fileparam.skiprows,\
                    header=None,names=self.fileparam.colNames,skipfooter=self.fileparam.skipfooter,na_values=self.fileparam.miss_val)
        except pd.errors.ParserError as e:
            raise WrongFormatError('CSV File {}: '.format(filename)+e.args[0])


        metadata={}
        
        for i,col in enumerate(df):
            metadata[col]={}
            if len(self.fileparam.unitNames)==len(df.columns):
                metadata[col]['unit']=self.fileparam.unitNames[i]
            else:
                metadata[col]['unit']=''

            if len(self.fileparam.miss_val)==len(df.columns):
                metadata[col]['null value']=self.fileparam.miss_val[i]
            else:
                metadata[col]['null value']=self.fileparam.miss_val

            metadata[col]['scale factor']=1
            metadata[col]['offset']=0
            metadata[col]['long name']=col
            metadata[col]['short name']=col


        p,f=os.path.split(filename)
        self.data[f]={}
        self.data[f]['path']=p
        self.data[f]['dataframe']=df
        self.data[f]['metadata']=metadata
    def _read_time(self):
        

        for key in self.data.keys():
            df=self.data[key]['dataframe']

            if self.fileparam.single_column is True:
                if self.fileparam.unit == 'auto':
                    time=pd.to_datetime(df[self.fileparam.time_col_name])
                elif self.fileparam.unit == 'matlab':
                    time=[matlab2datetime(tval) for tval in df['time']]
                elif self.fileparam.unit == 's' or self.unit == 'D':
                    time=pd.to_datetime(df[self.fileparam.time_col_name],unit=self.fileparam.unit)
                elif self.fileparam.unit == 'custom':
                    time=pd.to_datetime(df[self.fileparam.time_col_name],format=self.fileparam.customUnit)
                del df[self.fileparam.time_col_name]
            else:
                old_name=self.fileparam.time_col_name.keys()
                time=pd.to_datetime(df[old_name].rename(columns=self.fileparam.time_col_name))

                for oldkey in self.fileparam.time_col_name:
                    del df[self.fileparam.time_col_name[oldkey]]
                    del self.data[key]['metadata'][self.fileparam.time_col_name[oldkey]]

                
            df['time']=time
            self.data[key]['metadata']['time']={}
            self.data[key]['metadata']['time']['null value']=self.fileparam.miss_val
            self.data[key]['metadata']['time']['scale factor']=1
            self.data[key]['metadata']['time']['offset']=0
            self.data[key]['metadata']['time']['long name']='time'
            self.data[key]['metadata']['time']['short name']='time'
            self.data[key]['metadata']['time']['unit']='UTC'
            self.data[key]['dataframe']=df.set_index('time',inplace=True,drop=False)


    def _toToto(self):
        return self.data
