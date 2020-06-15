"""Read generic txt files.
Functions:
    read_generic: Read Spectra from SWAN ASCII file
    read_generics: Read multiple swan files into single Dataset
"""
import glob,os,sys
import pandas as pd
import datetime as dt
from PyQt5.QtWidgets import  QFileDialog
import numpy as np

class TRYAXISfile():

    @staticmethod
    def defaultExtensions():
        return ['.NONDIRSPEC','.DIRSPEC']


    def __init__(self,parent,data=[],metadata=[]):

        self.parent   =parent
        self.data=data
        self.metadata=metadata


        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        filt='TryAxys Files ('
        for ext in self.defaultExtensions():
            filt+='*'+ext+' '
        filt=filt[:-1]+')'

        self.filenames, _ = QFileDialog.getOpenFileNames(self.parent,"QFileDialog.getOpenFileName()", "",filt+";;All Files (*)", options=options)
        if not self.filenames:
             return

        # READ NONIRCSPCE
        if self.filenames[0].endswith('NONDIRSPEC'):
            self._reads_NONDIRSPEC()
        else:
            pass


    def _reads_NONDIRSPEC(self):
        for file in self.filenames:
            self._read_NONDIRSPEC(file)



    def _read_NONDIRSPEC(self,filename):
       
        try:
            with open(filename,'r',encoding=None) as f:
                df=pd.read_csv(f,sep='  ',skiprows=9,names=['freq','density'])
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
        df.set_index('freq',inplace=True)
        time=np.repeat(time,len(df.index), axis = 0)
        df['time']=time

        metadata={}
        metadata['index']={}
        metadata['index']['scale factor']=1
        metadata['index']['offset']=0
        metadata['index']['long name']='Freqeuncy'
        metadata['index']['unit']='Hz'

        metadata['density']={}
        metadata['density']['scale factor']=1
        metadata['density']['offset']=0
        metadata['density']['long name']='Spectral density'
        metadata['density']['unit']='m^2/Hz'

        metadata['time']={}
        metadata['time']['scale factor']=1
        metadata['time']['offset']=0
        metadata['time']['long name']='Time'
        metadata['time']['unit']='UTC'

        metadata['filename']=filename

        self.data.append(df)
        self.metadata.append(metadata)

    def _toDataFrame(self):
        #cols=['Alpha_[deg]','Cl_[-]','Cd_[-]','Cm_[-]']
        #dfs[name] = pd.DataFrame(data=..., columns=cols)
        #df=pd.DataFrame(data=,columns=) 
        return self.data


    def _toToto(self):
        return self.data,self.metadata
