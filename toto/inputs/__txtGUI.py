from PyQt5.QtWidgets import QApplication, QWidget, QPushButton,QHBoxLayout, QVBoxLayout,QComboBox,\
                             QLineEdit,QLabel,QToolButton,QMenu,QWidgetAction,QTextBrowser,QDialogButtonBox,\
                             QCheckBox,QFileDialog,QMainWindow,QDialog

from PyQt5.QtGui import QIntValidator
from PyQt5 import QtCore

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


class ImportGUI(QDialog):
    def __init__(self,TXTfile,parent=None):
        super(ImportGUI, self).__init__(parent)
        

        self.TXTfile=TXTfile

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        filt='TXT Files ('
        for ext in TXTfile.ext:
            filt+='*'+ext+', '
        filt=filt[:-2]+')'

        self.TXTfile.filename, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileName()", "",filt+";;All Files (*)", options=options)
        if not self.TXTfile.filename:
             self.close()



        Vlayout = QVBoxLayout()
        Hlayout = QHBoxLayout()
        ## number of Headerlines
        Hlayout.addWidget(QLabel('# of line before the data'))
        self.skiprows=QLineEdit(xstr(TXTfile.skiprows))
        self.skiprows.setValidator(QIntValidator())
        self.skiprows.setFixedWidth(30)
        Hlayout.addWidget(self.skiprows)
        Vlayout.addLayout(Hlayout)

        ## Header line
        Hlayout = QHBoxLayout()
        Hlayout.addWidget(QLabel('Header line'))
        self.colNamesLine=QLineEdit(xstr(TXTfile.colNamesLine))
        self.colNamesLine.setValidator(QIntValidator())
        self.colNamesLine.setFixedWidth(30)
        Hlayout.addWidget(self.colNamesLine)
        Vlayout.addLayout(Hlayout)


        ## Unit line
        Hlayout = QHBoxLayout()
        Hlayout.addWidget(QLabel('Unit line'))
        self.unitNamesLine=QLineEdit(xstr(TXTfile.unitNamesLine))
        self.unitNamesLine.setValidator(QIntValidator())
        self.unitNamesLine.setFixedWidth(30)
        Hlayout.addWidget(self.unitNamesLine)
        Vlayout.addLayout(Hlayout)


        ## skipfooter line
        Hlayout = QHBoxLayout()
        Hlayout.addWidget(QLabel('Footer line'))
        self.skipfooter=QLineEdit(xstr(TXTfile.skipfooter))
        self.skipfooter.setValidator(QIntValidator())
        self.skipfooter.setFixedWidth(30)
        Hlayout.addWidget(self.skipfooter)
        Vlayout.addLayout(Hlayout)


        ## Separator line
        Hlayout = QHBoxLayout()
        Hlayout.addWidget(QLabel('Separator'))
        self.sep = QComboBox()
        items=[',',';','tab','\s+']
        for item in items:
            self.sep.addItem(item)

        self.sep.setCurrentIndex(items.index('tab'))
        Hlayout.addWidget(self.sep)
        Vlayout.addLayout(Hlayout)

        ## skipfooter line
        Hlayout = QHBoxLayout()
        Hlayout.addWidget(QLabel('Missing values'))
        self.miss_val=QLineEdit(xstr(TXTfile.miss_val))
        self.miss_val.setFixedWidth(100)
        Hlayout.addWidget(self.miss_val)
        Vlayout.addLayout(Hlayout)
               

        Hlayout = QHBoxLayout()
        btn = QPushButton('Import')     
        btn.clicked.connect(self.import_input)
        Hlayout.addWidget(btn)

        btn = QPushButton('Cancel')     
        btn.clicked.connect(self.close)
        Hlayout.addWidget(btn)
        Vlayout.addLayout(Hlayout)

        self.setLayout(Vlayout)
    
        self.center_window()
        self.setWindowTitle('Parse data')
        self.exec_()

    def center_window(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def import_input(self):
        text = str(self.sep.currentText())
        
        self.TXTfile.sep=text.replace('tab','\t')

        self.TXTfile.skiprows=strx(self.skiprows.text())
        self.TXTfile.skipfooter=strx(self.skipfooter.text())
        self.TXTfile.colNamesLine=strx(self.colNamesLine.text())
        self.TXTfile.unitNamesLine=strx(self.unitNamesLine.text())

        self.close()

        return self.TXTfile

class parse_time_GUI(QDialog):
    def __init__(self,TXTfile,parent=None):
        super(parse_time_GUI, self).__init__(parent)
        

        self.TXTfile=TXTfile


        colNames=['None']
        colNames+=self.TXTfile.colNames
        

        mainVL = QVBoxLayout()

        ### Single time column
        self.checkBoxA = QCheckBox("Single columns")
        self.checkBoxA.setChecked(True)
        self.checkBoxA.stateChanged.connect(self.checkBoxAChangedAction)

        mainVL.addWidget(self.checkBoxA)
        timeHL = QHBoxLayout()

        timeHL.addWidget(QLabel('Time:'))
        self.single_time_column = QComboBox()
        for colName in self.TXTfile.colNames:
            self.single_time_column.addItem(colName)

        idx=[col for col in self.TXTfile.colNames if 'time' in col.lower()]
        if idx:
            idx=self.TXTfile.colNames.index(idx[0])
            self.single_time_column.setCurrentIndex(idx)

        timeHL.addWidget(self.single_time_column)
        mainVL.addLayout(timeHL)
        unitHL = QHBoxLayout()
        unitHL.addWidget(QLabel('unit'))
        units=['matlab','1970-01-01','auto','custom','s','D']
        self.unit_choice = QComboBox()
        
        for item in units:
            self.unit_choice.addItem(item)
        
        self.unit_choice.setCurrentIndex(2)
        unitHL.addWidget(self.unit_choice)
        self.customUnit=QLineEdit(self.TXTfile.customUnit)
        self.customUnit.setVisible(False)
        self.customUnit.setFixedWidth(200)
        self.unit_choice.currentIndexChanged.connect(self.display_custom)
        unitHL.addWidget(self.customUnit)
        mainVL.addLayout(unitHL)


        ### Multiple time column

        self.checkBoxB = QCheckBox("Multiple columns")
        self.checkBoxB.stateChanged.connect(self.checkBoxBChangedAction)
        mainVL.addWidget(self.checkBoxB)
              
        labels=['Year','Month','Day','Hour','Minute','Seconds']
        self.time_column=[]
        for label in labels:
            Hlayout = QHBoxLayout()
            Hlayout.addWidget(QLabel('%s:' % label))
            qc=QComboBox()
            for colName in colNames:
                qc.addItem(colName)
            idx=[col for col in colNames if label.lower() in col.lower()]
            if idx:
                idx=colNames.index(idx[0])
                qc.setCurrentIndex(idx)
            self.time_column .append( qc)
            Hlayout.addWidget(qc)
            mainVL.addLayout(Hlayout)

        
        Hlayout = QHBoxLayout()
        btn = QPushButton('Import')     
        btn.clicked.connect(self.import_input)
        Hlayout.addWidget(btn)

        btn = QPushButton('Cancel')     
        btn.clicked.connect(self.close)
        Hlayout.addWidget(btn)
        mainVL.addLayout(Hlayout)
        
        self.setLayout(mainVL)
    
        self.center_window()
        self.setFixedSize(400, 400)
        

        self.setWindowTitle('Parse time')
        self.show()
        self.exec_()

    def checkBoxAChangedAction(self,state):
        if (QtCore.Qt.Checked == state):
            self.checkBoxB.setChecked(False)
        else:
            self.checkBoxB.setChecked(True)

    def checkBoxBChangedAction(self,state):
        if (QtCore.Qt.Checked == state):
            self.checkBoxA.setChecked(False)
        else:
            self.checkBoxA.setChecked(True)
    
    def import_input(self):
        if self.checkBoxA.isChecked():
            self.TXTfile.single_column=True
            self.TXTfile.unit=self.unit_choice.currentText()
            self.TXTfile.customUnit=self.customUnit.text()
            self.TXTfile.time_col_name=self.single_time_column.currentText()
        
        else:

            self.TXTfile.single_column=False
            names=['year','month','day','hour','minute','second']
            self.TXTfile.time_col_name={}
            for i in range(0,len(self.time_column)):
                if self.time_column[i].currentText() !="None":
                    self.TXTfile.time_col_name[self.time_column[i].currentText()]=names[i]

        
        self.close()
        return self.TXTfile

    def display_custom():
        if self.unit_choice.currentIndex()==3:
            self.customUnit.setVisible(True)
        else:
            self.customUnit.setVisible(False)

    def center_window(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())