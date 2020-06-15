#!/usr/bin/python

"""
Toto main file
"""

import sys,os
import glob
from PyQt5 import uic
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QApplication,QListWidget,QAbstractItemView,QTreeWidgetItem,\
                            QVBoxLayout,QDialog,QHBoxLayout,QLabel,QLineEdit,QPushButton,QComboBox

from PyQt5.QtGui import QDoubleValidator 
import toto
from toto.core.cleaning import filled_gap,move_var,move_metadata
import copy

from time import mktime
from datetime import datetime, timedelta

import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

FORM_CLASS, _ = uic.loadUiType("mainwindow.ui")



def disconnect(signal, newhandler=None, oldhandler=None):
    while True:
        try:
            if oldhandler is not None:
                signal.disconnect(oldhandler)
            else:
                signal.disconnect()
        except TypeError:
            break
    if newhandler is not None:
        signal.connect(newhandler)

class EditFile(QDialog):

    def __init__(self, parent,index_name,filename='',varlist=[]):
        super(EditFile,self).__init__(parent)
        Vlayout = QVBoxLayout()

        Hlayout = QHBoxLayout()
        Hlayout.addWidget(QLabel('Change Index to:'))
        self.index = QComboBox()
        for var in varlist:
            self.index.addItem(var)
        Hlayout.addWidget(self.index)

        self.index.setCurrentIndex(varlist.index(index_name))

        Vlayout.addLayout(Hlayout)
        self.setLayout(Vlayout)
    
        self.center_window()
        self.setWindowTitle('Edit index from: %s' % filename)
    def center_window(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())    
    def exec(self):
        self.exec_()
        new_index=self.index.currentText()
        return new_index


class EditMetadata(QDialog):

    def __init__(self, parent,variable_name='',long_name='',unit='',null='NaN',scl_fac=1.,offset=0.,**kargs):
        super(EditMetadata,self).__init__(parent)
        Vlayout = QVBoxLayout()

        ## Long name
        Hlayout = QHBoxLayout()
        Hlayout.addWidget(QLabel('short name'))
        self.short_name=QLineEdit(variable_name)
        Hlayout.addWidget(self.short_name)
        Vlayout.addLayout(Hlayout)

        ## Long name
        Hlayout = QHBoxLayout()
        Hlayout.addWidget(QLabel('Long name'))
        self.long_name=QLineEdit(long_name)
        Hlayout.addWidget(self.long_name)
        Vlayout.addLayout(Hlayout)

        ## Unit
        Hlayout = QHBoxLayout()
        Hlayout.addWidget(QLabel('Unit'))
        self.unit=QLineEdit(unit)
        Hlayout.addWidget(self.unit)
        Vlayout.addLayout(Hlayout)

        ## Null value
        Hlayout = QHBoxLayout()
        Hlayout.addWidget(QLabel('Null value'))
        self.null=QLineEdit(null)
        Hlayout.addWidget(self.null)
        Vlayout.addLayout(Hlayout)

        ## Scale factor
        Hlayout = QHBoxLayout()
        Hlayout.addWidget(QLabel('Scale factor'))
        self.scl_fac=QLineEdit(str(scl_fac))
        self.scl_fac.setValidator(QDoubleValidator())
        Hlayout.addWidget(self.scl_fac)
        Vlayout.addLayout(Hlayout)

        ## Scale factor
        Hlayout = QHBoxLayout()
        Hlayout.addWidget(QLabel('Offset'))
        self.offset=QLineEdit(str(offset))
        self.offset.setValidator(QDoubleValidator())
        Hlayout.addWidget(self.offset)
        Vlayout.addLayout(Hlayout)

        self.setLayout(Vlayout)
    
        self.center_window()
        self.setWindowTitle('Variable: %s' % variable_name)
    
    def exec(self):
        self.exec_()
        metadata={}
        metadata['unit']=self.unit.text()
        metadata['null value']=self.null.text()
        metadata['scale factor']=float(self.scl_fac.text())
        metadata['offset']=float(self.offset.text())
        metadata['long name']=self.long_name.text()
        metadata['short name']=self.short_name.text()
        return metadata
    def center_window(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())




class TotoGUI(QMainWindow,FORM_CLASS):

    def __init__(self,data={}):
        super(TotoGUI,self).__init__()


        self.data=data
        self.databackup=copy.deepcopy(data)
        self.setupUi(self)
        
        # 
        self.fig1 = Figure()

        self.addmpl(self.fig1)
       
        self.initImport()
        self.initExport()
        self.initWindow()
        
        self.populate_gui()
        self.show()
        #self.list_file = CustomTreeWidget()
        self.list_file.itemChanged.connect (self.get_file_var)
        self.list_file.itemDropped.connect(self.move_variable_btw_file)
        self.list_file.editmetadata.connect(self.change_metadata)
        self.list_file.editfile.connect(self.edit_file)
        #self.list_file.setDragDropMode(QAbstractItemView.InternalMove)

        #self.list_file.dragLeaveEvent.connect(self.itemDropped)

    def edit_file(self,parent):

        variables=self.data[parent]['dataframe'].keys().tolist()
        old_name=self.data[parent]['dataframe'].index.name
        variables.append(old_name)
        ed=EditFile(self,old_name,filename=parent,varlist=variables)
        new_index=ed.exec()

        if new_index!=old_name:
            #self.data[parent]['dataframe'].reset_index( inplace=True)
            self.data[parent]['dataframe']=self.data[parent]['dataframe'].set_index(new_index,drop=False)  
            self.get_file_var([],[])  


        if self.data[parent]['dataframe'].index.name!='time':
            self.list_file.setDragEnabled(False)
        else:
            self.list_file.setDragEnabled(True)




            # =self.data[parent]['metadata'].pop(old_name)

    def change_metadata(self,item,parents,childs):
        metadata=self.data[parents]['metadata'][childs]
        ed=EditMetadata(self,variable_name=childs,long_name=metadata['long name'],\
            null=metadata['null value'],\
            scl_fac=metadata['scale factor'],**metadata)
        
        self.data[parents]['metadata'][childs]=ed.exec()
        new_name=self.data[parents]['metadata'][childs]['short name']

        self.data[parents]['metadata'][new_name]=self.data[parents]['metadata'].pop(childs)
        self.data[parents]['dataframe'].rename(columns={childs: new_name},inplace=True)

        self.list_file.rename(item,new_name)
        self.get_file_var([],[])

       



    def move_variable_btw_file(self,fIn,varIn,fOut):
        dfIn=self.data[fIn]['dataframe']
        dfOut=self.data[fOut]['dataframe']

        MIn=self.data[fIn]['metadata']
        MOut=self.data[fOut]['metadata']
            

        self.data[fIn]['dataframe'],self.data[fOut]['dataframe']=move_var(dfIn,varIn,dfOut)
        self.data[fIn]['metadata'],self.data[fOut]['metadata']=move_metadata(MIn,varIn,MOut)


    def addmpl(self, fig):
        self.canvas = FigureCanvas(fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas, 
                self.mplwindow, coordinates=True)
        self.mplvl.addWidget(self.toolbar)

    def rmmpl(self,):
        self.mplvl.removeWidget(self.canvas)
        self.canvas.close()
        self.mplvl.removeWidget(self.toolbar)
        self.toolbar.close()

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
            imp = QAction('%s file' % reader, self)
            imp.triggered.connect(self.callImport(reader))
            impMenu.addAction(imp)

        fileMenu.addMenu(impMenu)
            
        #
    def callImport(self,name):
        def imp():
            run_ft=self._import_from('toto.inputs.%s' % name,'%sfile' %name.upper())        
            file=run_ft(self)
            data=file._toToto()
            self.data.update(data)
            self.populate_gui(keys=list(data.keys()))
        return imp

    def initExport(self):
        pass
    def initWindow(self):
        #self.showMaximized()
        self.setWindowTitle('TOTO')

    def populate_gui(self,keys=None):
        #self.populate_list_file()
        self.populate_tree(keys)


   
    def populate_tree(self,keys):
        if keys is None:
            keys=self.data.keys()



        for file in keys:
            parent=self.list_file.addItem(file,"family")
            print(self.data[file]['metadata'].keys())

            for var in self.data[file]['metadata'].keys():
                self.list_file.addItem(var,"children",parent,self.data[file]['metadata'][var]['short name'])
  

        self.list_file.expandAll()

    def get_all_items(self):
        """Returns all QTreeWidgetItems in the given QTreeWidget."""
        check_vars = []
        checks_files=[]

        for i in range(self.list_file.topLevelItemCount()):
            top_item = self.list_file.topLevelItem(i)
            file=top_item.text(0)
            var=[]
            for j in range(top_item.childCount()):
                if (top_item.child(j).checkState(0) == Qt.Checked):# and (top_item.child(j).text(0)[:2] != 'No'):
                    var.append(top_item.child(j).text(0))

            check_vars.append(var)
            checks_files.append(file)



        return checks_files,check_vars


    def get_file_var (self,item, column): 

        checks_files,check_vars=self.get_all_items()
        self.refresh_plot(checks_files,check_vars)

        
        #self.list_file.blockSignals(False)

    def refresh_plot(self,File,Var):

        self.rmmpl()
        self.addmpl(self.fig1)
        
        self.fig1.clf()

        ax1f1 =self.fig1.add_subplot(111)
        
        for i,file in enumerate(File):
            for var in Var[i]:
                scl_fac=self.data[file]['metadata'][var]['scale factor']
                add_offset=self.data[file]['metadata'][var]['offset']
                index_name=self.data[file]['dataframe'].index.name
                x=self.data[file]['dataframe'].index
                y=((self.data[file]['dataframe'][var])*scl_fac)+add_offset
                ax1f1.plot(x,y,label=var)
                self.add_metadata(ax1f1,self.data[file]['metadata'][index_name],self.data[file]['metadata'][var])

    def add_metadata(self,ax,Xmetadata,Ymetadata):


        ax.set_ylabel(" %s [%s] " % (Ymetadata['long name'],Ymetadata['unit']))
        ax.set_xlabel(" %s [%s] " % (Xmetadata['long name'],Xmetadata['unit']))
        ax.legend()



def main():
    app = QApplication(sys.argv)
    import pandas as pd
    pd.plotting.register_matplotlib_converters()

    data={}

    filename='/home/remy/Calypso/Projects/004_Toto/test/txt/test1.txt'

    p,f=os.path.split(filename)
    data[f]={}
    data[f]['path']=p
    df=pd.read_csv(filename,sep='\t',skiprows=1,header=0,names=['year','month','day','hour','minute','second','depth','e','u','v'])
    df['time']=pd.to_datetime(df[['year','month','day','hour','minute','second']])
    del df['year']
    del df['month']
    del df['day']
    del df['hour']
    del df['minute']
    del df['second']
    df=df.set_index('time',drop=False)



    df=filled_gap(df,missing_value=np.NaN)


    data[f]['dataframe']=df
    data[f]['metadata']={}

    for col in df:
        if col=='time':
            data[f]['metadata'][col]={}
            data[f]['metadata'][col]['unit']='UTC'
            data[f]['metadata'][col]['null value']='NaN'
            data[f]['metadata'][col]['scale factor']=1
            data[f]['metadata'][col]['offset']=0
            data[f]['metadata'][col]['long name']='Time'
            data[f]['metadata'][col]['short name']=col
        else:

            data[f]['metadata'][col]={}
            data[f]['metadata'][col]['unit']='m.s-1'
            data[f]['metadata'][col]['null value']='NaN'
            data[f]['metadata'][col]['scale factor']=1
            data[f]['metadata'][col]['offset']=0
            data[f]['metadata'][col]['long name']='bla'
            data[f]['metadata'][col]['short name']=col

  
    filename='/home/remy/Calypso/Projects/004_Toto/test/txt/test2.txt'
    p,f=os.path.split(filename)
    data[f]={}
    data[f]['path']=p
    df2=pd.read_csv(filename,sep='\t',skiprows=1,header=0,names=['year','month','day','hour','minute','second','depth','em','um','vm'])
    df2['time']=pd.to_datetime(df2[['year','month','day','hour','minute','second']])
    del df2['year']
    del df2['month']
    del df2['day']
    del df2['hour']
    del df2['minute']
    del df2['second']
    df2=df2.set_index('time',drop=False)

    df2=filled_gap(df2,missing_value=np.NaN)
    data[f]['dataframe']=df2
    data[f]['metadata']={}

    for col in df2:
        if col=='time':
            data[f]['metadata'][col]={}
            data[f]['metadata'][col]['unit']='UTC'
            data[f]['metadata'][col]['null value']='NaN'
            data[f]['metadata'][col]['scale factor']=1
            data[f]['metadata'][col]['offset']=0
            data[f]['metadata'][col]['long name']='Time'
            data[f]['metadata'][col]['short name']=col
        else:

            data[f]['metadata'][col]={}
            data[f]['metadata'][col]['unit']='m.s-1'
            data[f]['metadata'][col]['null value']='NaN'
            data[f]['metadata'][col]['scale factor']=1
            data[f]['metadata'][col]['offset']=0
            data[f]['metadata'][col]['long name']='bla'
            data[f]['metadata'][col]['short name']=col

    ex = TotoGUI(data=data)
    # ex = TotoGUI(data=[df],metadata=[metadata])
    # ex = TotoGUI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()




