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
    print('')
    print('')
    sys.exit(-1)



#  GUI
from PyQt5.QtCore import Qt
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QApplication
from .message import *
from .plotting import Plotting
from .filemanip import EditFile,EditMetadata

# toto
import toto
from toto.totoframe import TotoFrame



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
        self.setWindowIcon(QtGui.QIcon(os.path.join(here,'..','_tools','toto.jpg')))
        
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
        self.reset_buttn.clicked.connect(self.reset_item)
    
    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Escape:
            self.close()
        if event.key() == 16777223: # delete key
            self.delete_selection()
            

    def load_df(self,dataframe,filename='dataset'):
        if isinstance(dataframe,pd.DataFrame):
            dataframe=[dataframe]

        filename=self.data.add_dataframe(dataframe,filename)
        return filename
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
                rep=yes_no_question('do you really want to delete var: %s' % item.text(0))
                if rep:
                    if self.data[item.parent().text(0)]['dataframe'].index.name==item.text(0):
                        display_error('the variable you are trying to delete is set as index\n'+\
                            'Change index and then delete the variable')
                        return

                    self.data.del_var(item.parent().text(0),item.text(0))
                    item.parent().removeChild(item)
            else:
                rep=yes_no_question('do you really want to delete file: %s' % item.text(0))
                if rep:
                    self.data.del_file(item.text(0))
                    item.removeChild(item)



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
        self.list_file.blocker.reblock()
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
    
    def get_all_out(self,reader):

        ext=''

        run_ft=self._import_from('toto.outputs.%s' % reader,'defaultExtensions')
        exs=run_ft()
        ext+='%s Files (*%s);;' % (reader,exs[0])

        ext+="All Files (*)"
        return ext,exs[0]

    def output_data(self,reader,filename):
        run_ft=self._import_from('toto.outputs.%s' % reader,'%sfile' %reader.upper())
        checks_files,_=self.list_file.get_all_items()
        df=run_ft(filename,[self.data[file] for file in checks_files])

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
                filenames=self.load_df(df,filename=filenames)
                self.list_file.populate_tree(self.data,keys=filenames)

        return imp
    def callOutput(self,name):
        def out():
            ext,exs=self.get_all_out(name)
            filename=put_file(self,ext,exs)
            if filename:
                # check if there is a GUI function
                self.output_data(name,filename)
        return out
    def initExport(self):
        # Main menu
        fileMenu=self.menu_File
        impMenu = QMenu('Export', self)
        # Look for all readers
        outputers=[d for d in dir(toto.outputs) if not d.startswith('_')]
        for outputer in outputers:
            im = QAction('%s file' % outputer, self)
            im.triggered.connect(self.callOutput(outputer))
            impMenu.addAction(im)

        fileMenu.addMenu(impMenu)
    def initWindow(self):
        #self.showMaximized()
        self.setWindowTitle('TOTO')

    def get_file_var (self):
        self.list_file.blocker.reblock()
        checks_files,check_vars=self.list_file.get_all_items()
        
        self.plotting.refresh_plot(self.data,checks_files,check_vars)
        self.list_file.blocker.unblock()

    
    def delete_selection(self):
        axes=self.plotting.sc.fig1.get_axes()
        ax=[ax for ax in axes if ax.get_gid()=='ax'][0]
        
        lines = [line for line in ax.lines if line.get_gid() and line.get_gid().startswith('selected')]
        for line in lines:
            x=line.get_xdata(orig=True)
            y=line.get_ydata(orig=True)
            label=line.get_gid().replace('selected_','').split(';')
            file=label[0]
            var=label[1]
            self.data.delete_data(file,var,xlim=[min(x),max(x)],ylim=[min(y),max(y)])


        self.get_file_var()

    def reset_item(self):
        item=self.list_file.currentItem()
        if item:
            if item.parent():
                rep=yes_no_question('do you really want to reset var: %s' % item.text(0))
                if rep:
                    self.data.reset(item.parent().text(0),varname=item.text(0))
            else:
                rep=yes_no_question('do you really want to reset file: %s' % item.text(0))
                if rep:
                    self.data.reset(item.parent().text(0),varname=None)


            self.get_file_var()
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

    sys.exit(app.exec_())



