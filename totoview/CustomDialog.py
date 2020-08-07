
from PyQt5.QtWidgets import QDialog,QGridLayout,QLabel,QCalendarWidget,QDialogButtonBox,QVBoxLayout,QLineEdit
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QDoubleValidator
from matplotlib.dates import date2num,num2date

def strx(s):
    if s is '':
        return None

    return float(s)

class PeaksDialog(QDialog):
    def __init__(self):
        super(PeaksDialog, self).__init__()
        self.paramters=['height','threshold','distance','prominence','width','wlen','rel_height','plateau_size']
        self.initUI()

    def initUI(self):
        Vl= QVBoxLayout()

        Grid = QGridLayout()
        
        self.param=[]
        for i,param in enumerate(self.paramters):
            Grid.addWidget(QLabel(param),i,0)
            ql=QLineEdit(None)
            ql.setValidator(QDoubleValidator())
            ql.setFixedWidth(100)
            Grid.addWidget(ql,i,1)
            self.param.append(ql)
        Vl.addLayout(Grid)
        self.buttons = QDialogButtonBox()
        self.ok_button = self.buttons.addButton( self.buttons.Ok )
        self.buttons.addButton( self.buttons.Cancel )
        self.buttons.accepted.connect( self.accept )
        Vl.addWidget(self.buttons)
       
        self.setLayout(Vl)
    
        self.setWindowTitle('Select peaks')

        self.setGeometry(300, 300, 250, 150)
        self.show()    

    def getResults(self):
        if self.exec_() == QDialog.Accepted:
            # get all values
            val={}
            for i,param in enumerate(self.paramters):
                val[param]=strx(self.param[i].text())
            
            return val
        else:
            return None

class CalendarDialog(QDialog):
    def __init__(self,xlim):
        super(CalendarDialog, self).__init__()
        self.initUI(xlim)
    def initUI(self,xlim):
        Vl= QVBoxLayout()

        Grid = QGridLayout()

        ## number of Headerlines
        Grid.addWidget(QLabel('Select start time'),0,0)
        Grid.addWidget(QLabel('Select end time'),0,1)
        xs=num2date(xlim[0])
        xt=num2date(xlim[1])
        xmin=QDate(xs.year, xs.month, xs.day)
        xmax=QDate(xt.year, xt.month, xt.day)
        self.tstart=QCalendarWidget()
        self.tstart.setDateRange(xmin, xmax)
        self.tstart.setSelectedDate(xmin)
        self.tend=QCalendarWidget()
        self.tend.setDateRange(xmin, xmax)
        self.tend.setSelectedDate(xmax)
        Grid.addWidget(self.tstart,1,0)
        Grid.addWidget(self.tend,1,1)
        Vl.addLayout(Grid)
        self.buttons = QDialogButtonBox()
        self.ok_button = self.buttons.addButton( self.buttons.Ok )
        self.buttons.addButton( self.buttons.Cancel )
        self.buttons.accepted.connect( self.accept )
        Vl.addWidget(self.buttons)

        
        self.setLayout(Vl)
    
        self.setWindowTitle('Select time')

        self.setGeometry(300, 300, 250, 150)
        self.show()

    def getResults(self):
        if self.exec_() == QDialog.Accepted:
            # get all values
            tstart = self.tstart.selectedDate().getDate()
            tend = self.tend.selectedDate().getDate()
            return tstart, tend
        else:
            return None