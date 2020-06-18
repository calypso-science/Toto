#!/usr/bin/python

"""
Toto main file
"""
from __future__ import division, unicode_literals, print_function, absolute_import
from builtins import map, range, chr, str
from future import standard_library
standard_library.install_aliases()

import numpy as np
import os,sys,glob 
import copy
try:
    import pandas as pd
except:
    print('')
    print('')
    print('Error: problem loading pandas package:')
    print('  - Check if this package is installed ( e.g. type: `pip install pandas`)')
    print('  - If you are using anaconda, try `conda update python.app`')
    print('  - If none of the above work, contact the developer.')
    print('')
    print('')
    sys.exit(-1)
    #raise


#  GUI
from PyQt5 import uic

from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QApplication
from .message import *
from .plotting import Plotting
from .filemanip import EditFile,EditMetadata

# toto
import toto
from toto.totoframe import TotoFrame
# from toto.core.cleaning import filled_gap,move_var,move_metadata,delete_variable,delete_file
# 

# from time import mktime
# from datetime import datetime, timedelta



here = os.path.dirname(os.path.abspath(__file__))
FORM_CLASS, _ = uic.loadUiType(os.path.join(here,'mainwindow.ui'))

PLOT_TYPE=['scatter','plot','bar','hist','rose','progressif']

class TotoGUI(QMainWindow,FORM_CLASS):

    def __init__(self,data=TotoFrame()):
        super(TotoGUI,self).__init__()

        if isinstance(data,TotoFrame):
            self.load_tf(data)

        if isinstance(data,pd.DataFrame):
            self.load_tf(TotoFrame())
            self.load_df(data)

        
        if isinstance(data,list):
            if isinstance(data[0],pd.DataFrame): 
                self.load_tf(TotoFrame())
                self.load_df(data)
            elif isinstance(data[0],str):
                self.load_files(data)
        
        if isinstance(data,str):
                self.load_files(data)


        
        self.databackup=copy.deepcopy(data)
        self.setupUi(self)
        
        # 
        self.plotting=Plotting(self.mplvl,self.plot_name)
       
        self.initImport()
        self.initExport()
        self.initWindow()
        self.initPlotType()
        
        self.list_file.populate_tree(self.data)
        self.show()

        self.list_file.itemChanged.connect(self.get_file_var)
        self.list_file.itemDropped.connect(self.move_variable_btw_file)
        self.list_file.editmetadata.connect(self.change_metadata)
        self.list_file.editfile.connect(self.edit_file)
        self.delete_buttn.clicked.connect(self.delete_item)


    def load_df(self,dataframe,filename='dataset'):
        if isinstance(dataframe,pd.DataFrame):
            dataframe=[dataframe]

        self.data.add_dataframe(dataframe,filename)

    def load_tf(self,totoframe):
        self.data=totoframe

    def load_files(self,filenames):
        if isinstance(filenames,str):
            filenames=[filenames]

        ext='.'+os.path.split(filenames[0])[-1].split('.')[-1]

        readers=[d for d in dir(toto.inputs) if not d.startswith('_')]
        gd_reader=False
        for reader in readers:
            run_ft=self._import_from('toto.inputs.%s' % reader,'%sfile' % reader.upper())
            exs=run_ft.defaultExtensions()
            if ext in exs:
                gd_reader=reader
                break

        if not gd_reader:
            display_error('could not find a reader for extension: %s' % ext) 
            sys.exit(-1)

        df=self.import_data(gd_reader,filenames)
        self.load_df(df,filename=filenames)
        self.list_file.populate_tree(self.data)




    def delete_item(self):
        item=self.list_file.currentItem()
        if item:
            if item.parent():
                delete_variable(item.parent().text())
            else:
                delete_file(item.text())



    def initPlotType(self):
        for item in PLOT_TYPE:
            self.plot_name.addItem(item)

        self.plot_name.setCurrentIndex(PLOT_TYPE.index('plot'))
        self.plot_name.activated.connect (self.get_file_var)


    def edit_file(self,parent):

        variables=self.data[parent]['dataframe'].keys().tolist()
        old_name=self.data[parent]['dataframe'].index.name
        # variables.append(old_name)
        ed=EditFile(self,old_name,filename=parent,varlist=variables)
        new_index=ed.exec()

        if new_index!=old_name:
            self.data[parent]['dataframe']=self.data[parent]['dataframe'].set_index(new_index,drop=False)  
            self.get_file_var()  


        if self.data[parent]['dataframe'].index.name!='time':
            self.list_file.setDragEnabled(False)
        else:
            self.list_file.setDragEnabled(True)



    def change_metadata(self,item,parents,childs):
        metadata=self.data[parents]['metadata'][childs]
        ed=EditMetadata(self,variable_name=childs,metadata=metadata)
        
        self.data[parents]['metadata'][childs]=ed.exec()
        new_name=self.data[parents]['metadata'][childs]['short_name']

        self.data[parents]['metadata'][new_name]=self.data[parents]['metadata'].pop(childs)
        self.data[parents]['dataframe'].rename(columns={childs: new_name},inplace=True)

        self.list_file.blocker.reblock()
        self.list_file.rename(item,new_name)
        self.list_file.blocker.unblock()
        self.get_file_var()



    def move_variable_btw_file(self,fIn,varIn,fOut):         
        self.data.move_var(fIn,fOut,varIn)


    def _get_file_list(self):
        return [metadata['filename'] for metadata in self.metadata]

    def _import_from(self,module, name):
        module = __import__(module, fromlist=[name])
        return getattr(module, name)

    def initImport(self):
        # Main menu
        fileMenu=self.menu_File
        impMenu = QMenu('Import', self)
        # Look for all readers
        readers=[d for d in dir(toto.inputs) if not d.startswith('_')]
        for reader in readers:
            im = QAction('%s file' % reader, self)
            im.triggered.connect(self.callImport(reader))
            impMenu.addAction(im)

        fileMenu.addMenu(impMenu)
        
        #

    def get_ext(self,reader):
        ext=''
        run_ft=self._import_from('toto.inputs.%s' % reader,'%sfile' % reader.upper())
        exs=run_ft.defaultExtensions()
        ext+='%s Files (' % reader
        for ex in exs:
            ext+='*'+ex+' '
        ext+=");;All Files (*)"
        return ext

    def import_data(self,reader,filenames):
        try:
            run_ft=self._import_from('totoview.inputs.%sGUI' % reader,'%sfile' %reader.upper())
            df=run_ft(self,filenames) 

        except:
            run_ft=self._import_from('toto.inputs.%s' % reader,'%sfile' %reader.upper()) 
            df=run_ft(filenames)

        return df._toDataFrame()
    def callImport(self,name):
        def imp():
            ext=self.get_ext(name)
            filenames=get_file(self,ext)
            if filenames:
                # check if there is a GUI function
                df=self.import_data(name,filenames)
                self.load_df(df,filename=filenames)
                self.list_file.populate_tree(self.data,keys=list(self.data.keys()))

        return imp

    def initExport(self):
        pass
    def initWindow(self):
        #self.showMaximized()
        self.setWindowTitle('TOTO')

    def get_file_var (self):
        self.list_file.blocker.reblock()
        checks_files,check_vars=self.list_file.get_all_items()
        
        self.plotting.refresh_plot(self.data,checks_files,check_vars)
        self.list_file.blocker.unblock()


        #self.list_file.blockSignals(False)

    

# --------------------------------------------------------------------------------}
# --- Mains 
# --------------------------------------------------------------------------------{
def showApp(firstArg=None,dataframe=None,filenames=[]):
    """
    The main function to start the data frame GUI.
    """
    app = QApplication(sys.argv)
    pd.plotting.register_matplotlib_converters()

    frame = TotoGUI()
    # Optional first argument
    if firstArg is not None:
        if isinstance(firstArg,list):
            filenames=firstArg
        elif isinstance(firstArg,str):
            filenames=[firstArg]
        elif isinstance(firstArg, pd.DataFrame):
            dataframe=firstArg
    #
    if (dataframe is not None) and (len(dataframe)>0):
        frame.load_df(dataframe)
    elif len(filenames)>0:
        frame.load_files(filenames)

    #ex = TotoGUI(data=data)
    # ex = TotoGUI(data=[df],metadata=[metadata])
    # ex = TotoGUI()
    sys.exit(app.exec_())


# def cmdline():
#     if len(sys.argv)>1:
#         totoview(filename=sys.argv[1])
#     else:
#         totoview()


# def main():
    
#     import pandas as pd
#     pd.plotting.register_matplotlib_converters()

#     data={}

#     filename='/home/remy/Calypso/Projects/004_Toto/test/txt/test1.txt'

#     p,f=os.path.split(filename)
#     data[f]={}
#     data[f]['path']=p
#     df=pd.read_csv(filename,sep='\t',skiprows=1,header=0,names=['year','month','day','hour','minute','second','depth','e','u','v'])
#     df['time']=pd.to_datetime(df[['year','month','day','hour','minute','second']])
#     del df['year']
#     del df['month']
#     del df['day']
#     del df['hour']
#     del df['minute']
#     del df['second']
#     df=df.set_index('time',drop=False)



#     df=filled_gap(df,missing_value=np.NaN)


#     data[f]['dataframe']=df
#     data[f]['metadata']={}

#     for col in df:
#         if col=='time':
#             data[f]['metadata'][col]={}
#             data[f]['metadata'][col]['unit']='UTC'
#             data[f]['metadata'][col]['null value']='NaN'
#             data[f]['metadata'][col]['scale factor']=1
#             data[f]['metadata'][col]['offset']=0
#             data[f]['metadata'][col]['long name']='Time'
#             data[f]['metadata'][col]['short name']=col
#         else:

#             data[f]['metadata'][col]={}
#             data[f]['metadata'][col]['unit']='m.s-1'
#             data[f]['metadata'][col]['null value']='NaN'
#             data[f]['metadata'][col]['scale factor']=1
#             data[f]['metadata'][col]['offset']=0
#             data[f]['metadata'][col]['long name']='bla'
#             data[f]['metadata'][col]['short name']=col

  
#     filename='/home/remy/Calypso/Projects/004_Toto/test/txt/test2.txt'
#     p,f=os.path.split(filename)
#     data[f]={}
#     data[f]['path']=p
#     df2=pd.read_csv(filename,sep='\t',skiprows=1,header=0,names=['year','month','day','hour','minute','second','depth','em','um','vm'])
#     df2['time']=pd.to_datetime(df2[['year','month','day','hour','minute','second']])
#     del df2['year']
#     del df2['month']
#     del df2['day']
#     del df2['hour']
#     del df2['minute']
#     del df2['second']
#     df2=df2.set_index('time',drop=False)

#     df2=filled_gap(df2,missing_value=np.NaN)
#     data[f]['dataframe']=df2
#     data[f]['metadata']={}

#     for col in df2:
#         if col=='time':
#             data[f]['metadata'][col]={}
#             data[f]['metadata'][col]['unit']='UTC'
#             data[f]['metadata'][col]['null value']='NaN'
#             data[f]['metadata'][col]['scale factor']=1
#             data[f]['metadata'][col]['offset']=0
#             data[f]['metadata'][col]['long name']='Time'
#             data[f]['metadata'][col]['short name']=col
#         else:

#             data[f]['metadata'][col]={}
#             data[f]['metadata'][col]['unit']='m.s-1'
#             data[f]['metadata'][col]['null value']='NaN'
#             data[f]['metadata'][col]['scale factor']=1
#             data[f]['metadata'][col]['offset']=0
#             data[f]['metadata'][col]['long name']='bla'
#             data[f]['metadata'][col]['short name']=col

#     ex = TotoGUI(data=data)
#     # ex = TotoGUI(data=[df],metadata=[metadata])
#     # ex = TotoGUI()
#     sys.exit(app.exec_())


# if __name__ == '__main__':
#     main()




