from PyQt5.QtWidgets import QApplication, QWidget, QPushButton,QHBoxLayout, QVBoxLayout,QComboBox,\
                             QLineEdit,QLabel,QToolButton,QMenu,QWidgetAction,QTextBrowser,QDialogButtonBox,\
                             QCheckBox,QFileDialog,QMainWindow,QDialog

from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt
from toto.inputs.txt import TXTfile as reader
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
    def __init__(self,TXTfile,parent,options):
        super(ImportGUI, self).__init__(parent)
        
        self.options=options
        
        Vlayout = QVBoxLayout()
        Hlayout = QHBoxLayout()
        ## number of Headerlines
        Hlayout.addWidget(QLabel('# of line before the data'))
        self.skiprows=QLineEdit(xstr(self.options['skiprows']))
        self.skiprows.setValidator(QIntValidator())
        self.skiprows.setFixedWidth(30)
        Hlayout.addWidget(self.skiprows)
        Vlayout.addLayout(Hlayout)

        ## Header line
        Hlayout = QHBoxLayout()
        Hlayout.addWidget(QLabel('Header line'))
        self.colNamesLine=QLineEdit(xstr(self.options['colNamesLine']))
        self.colNamesLine.setValidator(QIntValidator())
        self.colNamesLine.setFixedWidth(30)
        Hlayout.addWidget(self.colNamesLine)
        Vlayout.addLayout(Hlayout)


        ## Unit line
        Hlayout = QHBoxLayout()
        Hlayout.addWidget(QLabel('Unit line'))
        self.unitNamesLine=QLineEdit(xstr(self.options['unitNamesLine']))
        self.unitNamesLine.setValidator(QIntValidator())
        self.unitNamesLine.setFixedWidth(30)
        Hlayout.addWidget(self.unitNamesLine)
        Vlayout.addLayout(Hlayout)


        ## skipfooter line
        Hlayout = QHBoxLayout()
        Hlayout.addWidget(QLabel('Footer line'))
        self.skipfooter=QLineEdit(xstr(self.options['skipfooter']))
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
        self.miss_val=QLineEdit(xstr(self.options['miss_val']))
        self.miss_val.setFixedWidth(100)
        Hlayout.addWidget(self.miss_val)
        Vlayout.addLayout(Hlayout)
               

        # Hlayout = QHBoxLayout()
        # btn = QPushButton('Import')     
        # btn.clicked.connect(self.import_input)
        # Hlayout.addWidget(btn)

        # btn = QPushButton('Cancel')     
        # btn.clicked.connect(self.close)
        # Hlayout.addWidget(btn)
        # Vlayout.addLayout(Hlayout)

        self.setLayout(Vlayout)

        self.center_window()
        self.setWindowTitle('Parse data')
    def exec(self):
        self.exec_()
        self.import_input()
        return self.options

    def center_window(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def import_input(self):
        text = str(self.sep.currentText())

        self.options['sep']=text.replace('tab','\t')

        self.options['skiprows']=strx(self.skiprows.text())
        self.options['skipfooter']=strx(self.skipfooter.text())
        self.options['colNamesLine']=strx(self.colNamesLine.text())
        self.options['unitNamesLine']=strx(self.unitNamesLine.text())
        self.options['miss_val']=self.miss_val.text()
        self.close()

        return self.options

class parse_time_GUI(QDialog):
    def __init__(self,TXTfile,parent,options):
        super(parse_time_GUI, self).__init__(parent)
        
        self.options=options

        colNames=['None']
        colNames+=TXTfile.colNames
        

        mainVL = QVBoxLayout()

        ### Single time column
        self.checkBoxA = QCheckBox("Single columns")
        self.checkBoxA.setChecked(True)
        self.checkBoxA.stateChanged.connect(self.checkBoxAChangedAction)

        mainVL.addWidget(self.checkBoxA)
        timeHL = QHBoxLayout()

        timeHL.addWidget(QLabel('Time:'))
        self.single_time_column = QComboBox()
        for colName in TXTfile.colNames:
            self.single_time_column.addItem(colName)

        idx=[col for col in TXTfile.colNames if 'time' in col.lower()]
        if idx:
            idx=TXTfile.colNames.index(idx[0])
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
        self.customUnit=QLineEdit(self.options['customUnit'])
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

        
       
        self.setLayout(mainVL)
        self.setFixedSize(400, 400)
        self.center_window()
        
        

        self.setWindowTitle('Parse time')
        self.show()
    def exec(self):
        self.exec_()
        self.import_input()
        return self.options

    def checkBoxAChangedAction(self,state):
        if (Qt.Checked == state):
            self.checkBoxB.setChecked(False)
        else:
            self.checkBoxB.setChecked(True)

    def checkBoxBChangedAction(self,state):
        if (Qt.Checked == state):
            self.checkBoxA.setChecked(False)
        else:
            self.checkBoxA.setChecked(True)
    
    def import_input(self):
        if self.checkBoxA.isChecked():
            self.options['single_column']=True
            self.options['unit']=self.unit_choice.currentText()
            self.options['customUnit']=self.customUnit.text()
            self.options['time_col_name']=self.single_time_column.currentText()
        
        else:

            self.options['single_column']=False
            names=['year','month','day','hour','minute','second']
            self.options['time_col_name']={}
            for i in range(0,len(self.time_column)):
                if self.time_column[i].currentText() !="None":
                    self.options['time_col_name'][self.time_column[i].currentText()]=names[i]

 

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


class TXTfile():
    def __init__(self,parent,filename):
        
        self.fileparam=lambda:None

        self.parent   =parent
        self.filename     = filename


        options={}

        options['sep']          = '\t'
        options['colNames']     = []
        options['unitNames']     = []
        options['miss_val']    = 'NaN'


        options['colNamesLine'] = 1
        options['skiprows']     = 2
        options['unitNamesLine'] = 2
        options['skipfooter'] = 0

        options['single_column']=True
        options['unit']='s'
        options['customUnit']='%d-%m-%Y %H:%M:%S'

        options['time_col_name']={}

        self.encoding    = None


        # set usr defined parameter
        opt=ImportGUI(filename[0],self.parent,options)
        options=opt.exec()
        Re=reader(filename,**options) 
        Re.reads()   
        # # Parse the date
        opt=parse_time_GUI(Re.fileparam,self.parent,options)
        options=opt.exec()
        Re.fileparam.single_column=options['single_column']
        Re.fileparam.unit=options['unit']
        Re.fileparam.customUnit=options['customUnit']
        Re.fileparam.time_col_name=options['time_col_name']
        Re.read_time()
        self.Re=Re

    def _toDataFrame(self):
        return self.Re._toDataFrame()