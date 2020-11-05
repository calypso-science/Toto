import sys,os
from .create_frame import get_layout_from_sig,extract_option_from_frame

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog,QWidget,QFormLayout,QHBoxLayout,QStackedWidget,\
                            QVBoxLayout,QSpacerItem,QLabel,QPushButton,QApplication,QListWidget,QListWidgetItem,\
                            QLineEdit,QLabel,QGroupBox,QRadioButton,QButtonGroup,QScrollArea

from PyQt5.QtGui import QIntValidator,QDoubleValidator,QIcon,QFont
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as    NavigationToolbar
import matplotlib.pyplot as plt
import mplcyberpunk
import inspect


here = os.path.dirname(os.path.abspath(__file__)).replace('\\library.zip','')
class BaseWindow(QDialog):
    def __init__(self,folder=None,title='',logo=None, parent=None):
        super(BaseWindow, self).__init__(parent)

        self.resize(900,600)
        self.setWindowTitle(title)
        ssDir = os.path.join(here,"..", "_tools", "")
        if logo:
        	self.setWindowIcon(QIcon(logo))
        else:
        	self.setWindowIcon(QIcon(os.path.join(ssDir,'toto.ico')))    
       
        sshFile=os.path.join(ssDir,'TCobra.qss')
        with open(sshFile,"r") as fh:
            self.setStyleSheet(fh.read())

        
        self.opt=[]
        # Main window
        layout = QHBoxLayout()
        
        font = QFont()
        font.setFamily("Rod")
        font.setPointSize(23)

        # left pannel
        Left = QVBoxLayout()
        #Plotting Methods from Matplotlib
        with plt.style.context("cyberpunk"):
            self.figure = plt.figure()

            self.canvas = FigureCanvas(self.figure)
            self.canvas.setMaximumHeight(525)
            self.canvas.setMaximumHeight(725)
            self.toolbar = NavigationToolbar(self.canvas, self)

        
       #Labels
        self.label = QLabel(self)
        self.label.setFont(font)
        self.label.setText("  %s"%title)
        self.label.setMaximumSize(625,30)

        Left.addWidget(self.label)
        Left.addWidget(self.canvas)
        Left.addWidget(self.toolbar)


        # Right pannel

        Right = QVBoxLayout()
        label2 = QLabel(self)
        label2.setFont(font)
        label2.setText("Select Method:")
        Right.addWidget(label2)


        # Initisialize the methods
        self.method_names = QListWidget()
        self.method_names.currentRowChanged.connect(self.display)
        self.method_options=QStackedWidget()

        methods=self.init_folder(folder)

        for method in methods.keys():
            item=QListWidgetItem(method)
            self.method_names.addItem(item)
            self.method_options.addWidget(methods[method])


        Right.addWidget(self.method_names)
        #Right.addWidget(self.method_options)


        ## Slider
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.method_options)

        Right.addWidget(scroll)
        ## button

        bttn_box = QHBoxLayout()
        goPlot = QPushButton('Try')
        goPlot.setMaximumSize(60,20)
        goPlot.clicked.connect(self.filter)

        resetPlot = QPushButton('Reset')
        resetPlot.setMaximumSize(60,20)
        resetPlot.clicked.connect(self.reset)

        savePlot = QPushButton('Save')
        savePlot.setMaximumSize(60,20)
        savePlot.clicked.connect(self.save)

        cancelPlot = QPushButton('Cancel')
        cancelPlot.setMaximumSize(60,20)
        cancelPlot.clicked.connect(self.cancel)

        bttn_box.addWidget(goPlot)
        bttn_box.addWidget(resetPlot)
        bttn_box.addWidget(savePlot)
        bttn_box.addWidget(cancelPlot)
        # Vertically aligns the filte method
        Right.addLayout(bttn_box)


        layout.addLayout(Left)
        layout.addLayout(Right)

        self.setLayout(layout)

    def build_layout(self,sig):

        qw=QWidget()
 
        Vl,layout=get_layout_from_sig(sig)
        
        qw.setLayout(Vl)
        self.opt.append(layout)

        return qw
    def _import_from(self,module, name):
        module = __import__(module, fromlist=[name])
        return getattr(module, name)

    def init_folder(self,folder):
        ly={}
        readers=[d for d in dir(folder) if not d.startswith('_')]
        for reader in readers:
            fct=self._import_from('%s.%s' % (folder.__name__,reader),'%s' % reader)       
            sig=inspect.signature(fct)
            ly[reader]=self.build_layout(sig)
        return ly




    def display(self,i):
        self.method_options.setCurrentIndex(i)

    def get_options(self,pannel):

        opt=extract_option_from_frame(pannel)

        return opt


    def refresh_plot(self):
        with plt.style.context("cyberpunk"):
            self.figure.clf()
            ax = self.figure.add_subplot(111)

            ax.plot(self.X0[self.X[0].keys()[0]],label='original')
            ax.plot(self.X[0][self.X[0].keys()[0]],label='interpolated')
            plt.grid()
            self.figure.autofmt_xdate()
            ax.legend()
            self.canvas.draw()