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

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.dates import num2date

sys.path.append(os.path.dirname(os.path.abspath(__file__)))



from PyQt5.Qt import *

from PyQt5.uic import loadUiType
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, QMenu,QMenuBar, QApplication,QProxyStyle,QStyle,QStyleFactory
from .dialog.message import *
from .dialog.plotting import Plotting
from .dialog.filemanip import EditFile,EditMetadata

from .dialog.filtering import FiltWindow
from .dialog.interpolating import InterpWindow
from .dialog.selecting import SelectWindow

# toto
TOTO_PATH = os.getenv('TotoPath') #"C:\\Users\\remy\\Software\\Toto\\"
sys.path.append(TOTO_PATH)
try:
    import toto
except:
    print('')
    print('')
    print('Error: problem loading toto package:')
    print('  - Check if this package is installed ( e.g. type: `python setup_toto.py install`)')
    print('Or')
    print('  - Try setting up the toto path as environmental variable named: TotoPath ')
    print('')
    sys.exit(-1)



import toto.inputs
import toto.outputs
from toto.core.totoframe import TotoFrame,add_metadata_to_df
from toto.core.metadataframe import MetadataFrame
import platform
from ._tools import resource_rc

# Use NSURL as a workaround to pyside/Qt4 behaviour for dragging and dropping on OSx
op_sys = platform.system()
if op_sys == 'Darwin':
    from Foundation import NSURL

here = os.path.dirname(os.path.abspath(__file__))
FORM_CLASS, _ = loadUiType(os.path.join(here,'_tools','mainwindow.ui').replace('\\library.zip',''))

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

        ssDir = os.path.join(here, "_tools", "")

        sshFile=os.path.join(ssDir,'TCobra.qss').replace('\\library.zip','')
        with open(sshFile,"r") as fh:
            self.setStyleSheet(fh.read())


        
        self.databackup=copy.deepcopy(data)
        self.setupUi(self)
        self.setWindowIcon(QIcon(os.path.join(here,'_tools','toto.ico').replace('\\library.zip','')))
        
        # 
        self.plotting=Plotting(self.mplvl,self.plot_name)
       
        self.initImport()
        self.initExport()
        self.initDatamanip()
        self.initWindow()
        self.initPlotType()
        self.initHelp()
        self.initPlugins()
        
        self.list_file.populate_tree(self.data)
        self.show()

        self.list_file.itemChanged.connect(self.get_file_var)
        self.list_file.itemDropped.connect(self.move_variable_btw_file)
        self.list_file.editmetadata.connect(self.change_metadata)
        self.list_file.editfile.connect(self.edit_file)
        self.delete_buttn.clicked.connect(self.delete_item)
        self.reset_buttn.clicked.connect(self.reset_item)

        self.select_all_vars.clicked.connect(self.slc_vars)
        self.select_all_files.clicked.connect(self.slc_files)
        self.unselect_all.clicked.connect(self.unslc_all)

        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.StrongFocus)

    def _get_file_list(self):
        return [metadata['filename'] for metadata in self.metadata]

    def _import_from(self,module, name):
        module = __import__(module, fromlist=[name])
        return getattr(module, name)
#### INit
    def initPlugins(self):
        plugins=self._import_from('toto','plugins')
        for plugin in [x for x in dir(plugins) if not x.startswith('_')]:
            acts=self._import_from('toto.plugins',plugin)
            plugMenu=QMenu(plugin, self)

            for act in [x for x in dir(acts) if not x.startswith('_')]:
                im = QAction(act.replace('_',' ').capitalize(), self)
                im.triggered.connect(self.CallWrapper([plugin,act]))
                plugMenu.addAction(im)


            self.menubar.addMenu(plugMenu)


    def initHelp(self):
        Bar_help=QMenuBar(self)
        fileMenu=QMenu('Help',self)

        im = QAction('Shortcuts', self)
        im.triggered.connect(show_help_shortcuts)
        fileMenu.addAction(im)
        im = QAction('Help', self)
        im.triggered.connect(self.help_browser)
        fileMenu.addAction(im)
        Bar_help.addMenu(fileMenu)
        self.menubar.setCornerWidget(Bar_help)

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

    def initPlotType(self):
        for item in PLOT_TYPE:
            self.plot_name.addItem(item)

        self.plot_name.setCurrentIndex(PLOT_TYPE.index('plot'))
        self.plot_name.activated.connect (self.get_file_var)
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
        
    def initDatamanip(self):
        datamanip=self.menuData_manipulation
        im = QAction('Data selector', self)
        im.triggered.connect(self.callSelect)
        datamanip.addAction(im)

        im = QAction('Data filter', self)
        im.triggered.connect(self.callFilter)
        datamanip.addAction(im)

        im = QAction('Data interpolator', self)
        im.triggered.connect(self.callInterp)
        datamanip.addAction(im)

        im = QAction('Combined files', self)
        im.triggered.connect(self.callCombine)
        datamanip.addAction(im)
        
#### Events
    def callCombine(self):
        mss=show_list_file(list(self.data.keys()))
        files=mss.exec()
        self.data.combine_dataframe(files)
        self.list_file.blocker.reblock()
        self.list_file.populate_tree(self.data)
        self.get_file_var()
        self.list_file.blocker.unblock()
    def CallWrapper(self,module):
        def out():
            self.list_file.blocker.reblock()
            checks_files,check_vars,checks_dataframe=self.list_file.get_all_items()
            # check selected all slected file                
            data_to_process=[]
            for file in checks_dataframe:
                self.data[file]['filename']=file
                data_to_process.append(self.data[file])

            fct=self._import_from('toto.plugins.%s'% module[0],module[1])
            if len(data_to_process)>0:
                sc=wrapper_plugins(data_to_process,fct)
                dfout=sc.exec()
                if dfout:
                    for i,df in enumerate(dfout):
                        if (len(df.index) != len(data_to_process[i]['dataframe'].index)) or\
                               (df.index[0]!=data_to_process[i]['dataframe'].index[0]):

                            self.data.add_dataframe([df],[checks_dataframe[i]+'_new'])
                        else:
                            self.data.replace_dataframe([checks_dataframe[i]],[dfout[i]])

                    
                self.list_file.populate_tree(self.data)
                self.list_file.check_item(checks_dataframe)
                checks_files_after,check_vars_after,checks_dataframe_after=self.list_file.get_all_items()
                self.plotting.refresh_plot(self.data,checks_files_after,check_vars_after)
                
            else:
                display_error('You need to select at least on file')
            self.list_file.blocker.unblock()
        return out

    def help_browser(self):
        mss=show_help_browser()
        mss.exec_()
    def callSelect(self):

        self.list_file.blocker.reblock()
        checks_files,check_vars,checks_dataframe=self.list_file.get_all_items()

        if len(checks_dataframe)<1:
            display_error('You need to select at least one variable and one file')
            return        

        data_to_filter=[]
        to_del=[]
        for i,file in enumerate(checks_files):
            df=self.data[file]['dataframe']
            check = np.isin(check_vars[i], df.columns)
            if np.all(check) and len(check_vars[i])>=1 and file in checks_dataframe:
                data_to_filter.append(df[check_vars[i]])
            else:
                to_del.append(i)

        if len(to_del)>0:
            for i in sorted(to_del, reverse = True):
                del checks_files[i]
                del check_vars[i]


        if len(checks_files)<1 or len(data_to_filter)<1:
            display_error('The selected variable is not present in the selected file')
            return        
       


        main = SelectWindow(data_to_filter) 

        df=main.exec()

        self._update(checks_files,df)

        self.list_file.populate_tree(self.data)
        self.plotting.refresh_plot(self.data,checks_files,check_vars)
        self.list_file.blocker.unblock()

    def callInterp(self):
        self.list_file.blocker.reblock()
        checks_files,check_vars,checks_dataframe=self.list_file.get_all_items()

        if len(checks_dataframe)<1:
            display_error('You need to select at least one variable and one file')
            return        

        data_to_filter=[]
        to_del=[]
        for i,file in enumerate(checks_files):
            df=self.data[file]['dataframe']
            check = np.isin(check_vars[i], df.columns)
            if np.all(check) and len(check_vars[i])>=1 and file in checks_dataframe:
                data_to_filter.append(df[check_vars[i]])
            else:
                to_del.append(i)

        if len(to_del)>0:
            for i in sorted(to_del, reverse = True):
                del checks_files[i]
                del check_vars[i]


        if len(checks_files)<1 or len(data_to_filter)<1:
            display_error('The selected variable is not present in the selected file')
            return        
               
       
        main = InterpWindow(data_to_filter) 
        df=main.exec()
        for i,file in enumerate(checks_files):
            self.data[file]['dataframe'][check_vars[i]]=df[i]
        self.plotting.refresh_plot(self.data,checks_files,check_vars)
        self.list_file.blocker.unblock()

    def callFilter(self):
        self.list_file.blocker.reblock()
        checks_files,check_vars,checks_dataframe=self.list_file.get_all_items()

        if len(checks_dataframe)<1:
            display_error('You need to select at least one variable and one file')
            return        

        data_to_filter=[]
        LonLat=[]
        to_del=[]
        for i,file in enumerate(checks_files):
            df=self.data[file]['dataframe']
            check = np.isin(check_vars[i], df.columns)
            if np.all(check) and len(check_vars[i])>=1 and file in checks_dataframe:
                data_to_filter.append(df[check_vars[i]])
                LonLat.append([self.data[file]['longitude'],self.data[file]['latitude']])
            else:
                to_del.append(i)

        if len(to_del)>0:
            for i in sorted(to_del, reverse = True):
                del checks_files[i]
                del check_vars[i]


        if len(checks_files)<1 or len(data_to_filter)<1:
            display_error('The selected variable is not present in the selected file')
            return        
       
        main = FiltWindow(data_to_filter,LonLat=LonLat) 
        df=main.exec()
        for i,file in enumerate(checks_files):
            self.data[file]['dataframe'][check_vars[i]]=df[i]
        self.plotting.refresh_plot(self.data,checks_files,check_vars)
        self.list_file.blocker.unblock()


    def callImport(self,name):
        def imp():
            ext=self.get_ext(name)
            filenames=get_file(self,ext)
            if filenames:
                # check if there is a GUI function
                df=self.import_data(name,filenames)
                filenames=self.load_df(df,filename=filenames)
                self.list_file.populate_tree(self.data)#,keys=filenames)

        return imp
    def callOutput(self,name):
        def out():
            ext,exs=self.get_all_out(name)
            filename=put_file(self,ext,exs)
            if filename:
                # check if there is a GUI function
                self.output_data(name,filename)
        return out
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        """
        Drop files directly onto the widget
        File locations are stored in fname
        :param e:
        :return:
        """
        if e.mimeData().hasUrls:
            e.setDropAction(Qt.CopyAction)
            e.accept()
            # Workaround for OSx dragging and dropping
            for url in e.mimeData().urls():
                if op_sys == 'Darwin':
                    fname = str(NSURL.URLWithString_(str(url.toString())).filePathURL().path())
                else:
                    fname = str(url.toLocalFile())

            
            self.load_files(fname)
        else:
            e.ignore()

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Escape:
            self.close()
        if event.key() == 16777223: # delete key
            self.delete_selection()

        if event.key() ==16777220 or event.key() ==16777221: # Enter key
            self.add_selection()

        if event.key() == 16777264: # Press F1
            mss=show_help_browser()
            mss.exec_()
        if event.key() == 16777265: # Press F2
            show_help_shortcuts()


#### loading                   
    def _update(self,checkfiles,df):
        for i,file in enumerate(checkfiles):
            for key in df[i].keys():
                if key not in self.data[file]['dataframe']:
                    self.data[file]['metadata'].update(MetadataFrame(key))
                self.data[file]['dataframe'][key]=df[i][key]

    def load_df(self,dataframe,filename=['dataset']):
        if isinstance(dataframe,pd.DataFrame):
            dataframe=[dataframe]

        filename=self.data.add_dataframe(dataframe,filename)
        self.list_file.populate_tree(self.data)
        self.get_file_var()

        return filename
    def load_tf(self,totoframe):
        self.data=totoframe

    def load_files(self,filenames):
        if isinstance(filenames,str):
            filenames=[filenames]

        ext='.'+os.path.split(filenames[0])[-1].split('.')[-1]

        readers=[d for d in dir(toto.inputs) if not d.startswith('_')]
        gd_reader=[]
        for reader in readers:
            run_ft=self._import_from('toto.inputs.%s' % reader,'%sfile' % reader.upper())
            exs=run_ft.defaultExtensions()
            if ext in exs:
                gd_reader.append(reader)
                

        if len(gd_reader)<1:
            display_error('could not find a reader for extension: %s' % ext) 
            sys.exit(-1)

        if len(gd_reader)>1:
            readername=['%sfile' %reader.upper() for reader in gd_reader]
            mss=show_list_file(readername,title='Choose a reader',multiple=False)
            reader=mss.exec()
            if reader is None:
                return
            if len(reader)==0:
                reader=[readername[0]]
                

            gd_reader=reader[0].replace('file','').lower()

        if isinstance(gd_reader,list):
            gd_reader=gd_reader[0]    
        df=self.import_data(gd_reader,filenames)
        self.load_df(df,filename=filenames)

## file manip
    def unslc_all(self):
        self.list_file.auto_check(unchecked=True)
        self.get_file_var()
    def slc_vars(self):
        self.list_file.auto_check(all_vars=True)
        self.get_file_var()
    def slc_files(self):
        self.list_file.auto_check(all_file=True)
        self.get_file_var()

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
        _,_,checks_dataframe=self.list_file.get_all_items()
        if len(checks_dataframe)>0:
            df=run_ft(filename,[self.data[file] for file in checks_dataframe])
        else:
            display_error('You need to select at least on file')

    def import_data(self,reader,filenames):
        try:
            run_ft=self._import_from('totoview.inputs.%sGUI' % reader,'%sfile' %reader.upper())
            df=run_ft(self,filenames) 

        except:
            run_ft=self._import_from('toto.inputs.%s' % reader,'%sfile' %reader.upper()) 
            df=run_ft(filenames)

        return df._toDataFrame()



    def get_file_var (self):
        self.list_file.blocker.reblock()
        checks_files,check_vars,checks_dataframe=self.list_file.get_all_items()
        
        self.plotting.refresh_plot(self.data,checks_files,check_vars)
        self.list_file.blocker.unblock()

    def add_selection(self):
        axes=self.plotting.sc.fig1.get_axes()
        ax=[ax for ax in axes if ax.get_gid()=='ax'][0]       
        lines = [line for line in ax.lines if line.get_gid() and line.get_gid().startswith('selected')]


        for line in lines:
            x=line.get_xdata(orig=True)
            y=line.get_ydata(orig=True)
            if len(x)<1:
                continue
            label=line.get_gid().replace('selected_','').split(';')
            file=label[0]
            var=label[1]
            self.data.delete_data(file,var,xlim=[min(x),max(x)],ylim=[min(y),max(y)])
            df=pd.DataFrame({self.data[file]['dataframe'].index.name:num2date(x),var:y})
            df[self.data[file]['dataframe'].index.name] = pd.to_datetime(df[self.data[file]['dataframe'].index.name]).dt.tz_localize(None)
            df.set_index(self.data[file]['dataframe'].index.name,inplace=True,drop=False)
            self.data.add_dataframe([df],['selection_'+file])
            self.list_file.populate_tree(self.data)

        self.get_file_var()
    def delete_selection(self):
        axes=self.plotting.sc.fig1.get_axes()
        ax=[ax for ax in axes if ax.get_gid()=='ax'][0]
        
        lines = [line for line in ax.lines if line.get_gid() and line.get_gid().startswith('selected')]
        for line in lines:
            x=line.get_xdata(orig=True)
            y=line.get_ydata(orig=True)
            if len(x)<1:
                continue
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
                    self.data.reset(item.text(0),varname=None)

            self.list_file.populate_tree(self.data)
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



