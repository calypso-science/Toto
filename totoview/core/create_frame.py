import datetime #import datetime
import dateutil

from PyQt5.QtWidgets import QFormLayout,QHBoxLayout,QStackedWidget,QWidget,QPushButton,QFileDialog,\
                            QVBoxLayout,QSpacerItem,QLabel,QPushButton,QApplication,QListWidget,QListWidgetItem,\
                            QLineEdit,QLabel,QGroupBox,QRadioButton,QButtonGroup,QScrollArea,QDateTimeEdit,QComboBox

from PyQt5.QtGui import QIntValidator,QDoubleValidator
import os
def pick_dir(wd):
    def cmd():
        dialog = QFileDialog()
        folder_path = dialog.getExistingDirectory(None, "Select Folder")
        wd.setText(folder_path)
    return cmd

def strx(s,validator):
    if s is '':
        val= None
    elif isinstance(validator,QIntValidator):
        val=int(s)
    elif isinstance(validator,QDoubleValidator):
        val=float(s)
    else:
        try:
            if len(s.split(' '))>0:
                val=[float(s) for s in s.split(' ')]
        except:
            val=s


    return val

def get_layout_from_sig(sig):

    Vl = QFormLayout()
    layout={}

    args=sig.parameters['args'].default
    I=0
    for arg in args.keys():
        #l = QLabel(arg)
        #Vl.addRow(l)
        
        if isinstance(args[arg],dict):
            # box=QButtonGroup()
            box=QComboBox()
            bx={}
            for i,key in enumerate(args[arg].keys()):
                box.addItem(key)
                if args[arg][key]:
                    box.setCurrentIndex(i)
            #     qr=QRadioButton(key)
            #     qr.setChecked(args[arg][key])
            #     box.addButton(qr)
            #     Vl.addWidget(qr)
            #bx[key]=box
            Vl.addRow(arg,box)
            layout[arg]=box
        else:
            wd=QLineEdit('')
            if isinstance(args[arg],int):
                wd.setValidator(QIntValidator())
                wd.setText(str(args[arg]))
            elif isinstance(args[arg],float):
                wd.setValidator(QDoubleValidator())
                wd.setText(str(args[arg]))
            elif hasattr(args[arg],'year'):
                wd=QDateTimeEdit() 
                wd.setDisplayFormat("dd/MM/yyyy hh:mm:ss")
            elif isinstance(args[arg],str):
                wd.setText(args[arg])

            elif isinstance(args[arg],list):
                wd.setText(' '.join([str(i) for i in args[arg]])) 
               
            if isinstance(args[arg],str) and os.path.isdir('/tmp/'):
                container=QWidget()
                ly=QHBoxLayout()
                ly.addWidget(wd)
                bttn=QPushButton('...')
                bttn.clicked.connect(pick_dir(wd))
                ly.addWidget(bttn)
                container.setLayout(ly)
                Vl.addRow(arg,container)
            else:
                Vl.addRow(arg,wd,)

            layout[arg]=wd
    return Vl,layout
def extract_option_from_frame(pannel):

    opt={}
    for key in pannel.keys():
        if isinstance(pannel[key],QLineEdit):
            opt[key]=strx(pannel[key].text(),pannel[key].validator())
        elif isinstance(pannel[key],QRadioButton):
            opt[key]=pannel[key].isChecked()
        elif isinstance(pannel[key],QComboBox):
            opt[key]=pannel[key].currentText()            
        elif isinstance(pannel[key],QDateTimeEdit):
            dt = pannel[key].dateTime()
            dt_string = dt.toString(pannel[key].displayFormat())
            opt[key]=dateutil.parser.parse(dt_string,dayfirst=True)

        elif isinstance(pannel[key],dict):
            sub={}
            for children in pannel[key]:
                sub[children]=pannel[key][children].isChecked()
            opt[key]=sub

    return opt