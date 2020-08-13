
import os
from PyQt5.QtWidgets import QWidget,QScrollArea,QComboBox,QPushButton,QMessageBox,QFileDialog,QDialog,QTreeWidgetItem,QTreeWidget,QHBoxLayout,QVBoxLayout,QTextBrowser,QFormLayout
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
import toto
import inspect
from ..core.create_frame import get_layout_from_sig,extract_option_from_frame
import pandas as pd
from toto.core.totoframe import add_metadata_to_df

HERE = os.path.dirname(os.path.abspath(__file__))

def display_warning(txt):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText(txt)
    msg.setWindowTitle("Warning")
    msg.show()
    msg.exec_()

def display_error(txt):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(txt)
    msg.setWindowTitle("Error")
    msg.show()
    msg.exec_()

def yes_no_question(txt):
    # Create a confirmation dialog asking for permission to quit the application:
    box = QMessageBox()
    box.setIcon(QMessageBox.Question)
    box.setWindowTitle('confirmation')
    box.setText(txt)
    box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    box.setDefaultButton(QMessageBox.No)
    buttonYes = box.button(QMessageBox.Yes)
    buttonYes.setText('OK')
    buttonNo = box.button(QMessageBox.No)
    buttonNo.setText('Cancel')
    box.exec_()

    # Executing a routine for quitting the application:
    if box.clickedButton() == buttonYes:
        return True
    else:
        return False

def get_file(parent,ext):
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    filenames, _ = QFileDialog.getOpenFileName(parent,"QFileDialog.getOpenFileName()", "",ext, options=options)
    if filenames=='':
        return None

    if isinstance(filenames,str):
        filenames=[filenames]
    if not filenames:
         return
    else:
        return filenames

def put_file(parent,ext,exs):
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    filenames, _ = QFileDialog.getSaveFileName(parent,"QFileDialog.getSaveFileName()", "",ext, options=options)
    if filenames=='':
        return None
    if not filenames:
         return
    else:
        if not filenames.endswith(exs):
            filenames+=exs
        return filenames

def show_help_shortcuts():
    box = QMessageBox()
    box.setIcon(QMessageBox.Information)
    box.setWindowTitle('Shortcuts')
    txt='Shortcuts list:\n'+\
        ' d     => delete seclection\n'+\
        ' enter => save seclection in new file\n'+\
        ' F1    => display help\n'+\
        ' F2    => display this message\n'

    box.setText(txt)
    box.show()
    box.exec_()

class wrapper_plugins(QDialog):
    def __init__(self,tfs,fct, parent=None):
        super(wrapper_plugins, self).__init__(parent)
        self.fct=fct
        self.tfs=tfs
        self.dfs=[x['dataframe'] for x in tfs]
        self.mets=[x['metadata'] for x in tfs]
        self.var_list=[]

        for df in self.dfs:
            self.var_list+=list(df.keys())

        self.resize(400,600)
        self.setWindowTitle(fct.__name__)
        ssDir = os.path.join(HERE,"..","..", "_tools", "")
        self.setWindowIcon(QIcon(os.path.join(ssDir,'toto.jpg')))    
           
        sshFile=os.path.join(ssDir,'TCobra.qss')
        with open(sshFile,"r") as fh:
            self.setStyleSheet(fh.read())
        
        sig=inspect.signature(fct)

        layout=QVBoxLayout()


        ## Top frame with function inputs
        vars_in=self._get_inputs_from_sig(sig)
        top,ly=self._create_input_frame(vars_in,self.var_list)
        qw=QWidget()
        qw.setLayout(top)
        scroll_top = QScrollArea()
        scroll_top.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scroll_top.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scroll_top.setWidgetResizable(True)
        scroll_top.setWidget(qw)

        ## Bottom frame with function options
        bottom,opt=get_layout_from_sig(sig)
        qw=QWidget()
        qw.setLayout(bottom)
        scroll_bot = QScrollArea()
        scroll_bot.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scroll_bot.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scroll_bot.setWidgetResizable(True)
        scroll_bot.setWidget(qw)

        bttn_box = QHBoxLayout()
        go = QPushButton('Save')
        go.setMaximumSize(60,20)
        go.clicked.connect(self.go)

        cancel = QPushButton('Cancel')
        cancel.setMaximumSize(60,20)
        cancel.clicked.connect(self.cancel)

        bttn_box.addWidget(go)
        bttn_box.addWidget(cancel)

        layout.addWidget(scroll_top)
        layout.addWidget(scroll_bot)
        layout.addLayout(bttn_box)
        self.setLayout(layout)
        self.opt=opt
        self.varin=ly
    def _get_inputs_from_sig(self,sig):
        return [x for x in sig.parameters if (x!='args') and (x!='self')]
    def _create_input_frame(self,vars_in,var_list):
        var_list_lw=['none']
        var_list_lw+=[x.lower() for x in var_list]
        var_list=['none']+var_list

        Vl = QFormLayout()
        layout={}
        for Vars in vars_in:
            box=QComboBox()
            layout[Vars]=box
            for var in var_list:
                box.addItem(var)

            if Vars.lower() in var_list_lw:
                box.setCurrentIndex(var_list_lw.index(Vars.lower()))
            else:
                box.setCurrentIndex(0)
            Vl.addRow(Vars,box)
        return Vl,layout
    def get_variables(self):
        varin={}
        for var in self.varin:
            txt=self.varin[var].currentText()
            if txt!='none':
                varin[var]=txt

        return  {v: k for k, v in varin.items()}


    def cancel(self):
        self.dfs=0
        self.close()
        
        
    def go(self):
        opt=extract_option_from_frame(self.opt)
        var=self.get_variables()
        access=self.fct.__repr__().split(' ')[1].split('.')[0]

        for i,df in enumerate(self.dfs):
            index_name=df.index.name
            df1=df.rename(columns=var)
            mets=self.mets[i].copy()
            for key in var:
                mets[var[key]] = mets.pop(key)

            ## add all metadata here so it is passed inside the function
            ## Must be used before they disappear
            df1=add_metadata_to_df(df1,mets)
            df1.longitude=self.tfs[i]['longitude']
            df1.latitude=self.tfs[i]['latitude']
            df1.filename=self.tfs[i]['filename']

            F=getattr(getattr(df1, access),self.fct.__name__)

#            dfout=F(args=opt)
            try:
                dfout=F(args=opt)
            except Exception as exc:
                display_error("Cannot run {} function:\n{}".format(self.fct.__name__, exc))
                self.close()
                return

            if isinstance(dfout,pd.DataFrame):
                del df[index_name]
                self.dfs[i] = pd.merge_asof(df, dfout, on=index_name).set_index(index_name,drop=False)
            elif isinstance(dfout,str):
                display_error("Cannot run {} function:\n{}".format(self.fct.__name__, dfout))
                self.close()
            
        self.close()
    def exec(self):
        self.exec_()
        return self.dfs

class show_help_browser(QDialog):
    def __init__(self, parent=None):
        super(show_help_browser, self).__init__(parent)


        self.resize(900,600)
        self.setWindowTitle('Functions help')
        ssDir = os.path.join(HERE,"..","..", "_tools", "")
        self.setWindowIcon(QIcon(os.path.join(ssDir,'toto.jpg')))    
           
        sshFile=os.path.join(ssDir,'TCobra.qss')
        with open(sshFile,"r") as fh:
            self.setStyleSheet(fh.read())


        layout=QHBoxLayout()
        self.tree = QTreeWidget()
        layout.addWidget(self.tree)
        
        self.message = QTextBrowser()
        layout.addWidget(self.message)

        self.setLayout(layout)
        self.initTree()

        self.tree.selectionModel().selectionChanged.connect(self.update_message)

    def initTree(self):
        all_dirs=dir(toto)
        modules=[x for x in all_dirs if not x.startswith('_') and x != 'core']
        for module in modules:
            parent = QTreeWidgetItem(self.tree.invisibleRootItem())
            parent.setText(0, module)
            fcts = dir(getattr(toto,module))
            fcts=[x for x in fcts if not x.startswith('_')]
            for fct in fcts:
                child = QTreeWidgetItem(parent)
                child.setText(0, fct)

        self.tree.expandAll()
        self.tree.setHeaderLabel('Module')


    def update_message(self):
        item=self.tree.currentItem()
        if item:
            if item.parent():
                module=item.parent().text(0)
                fct=item.text(0)
                f=getattr(getattr(toto,module),fct)
                mms=inspect.getdoc(f)
                self.message.setText(mms)


