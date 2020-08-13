
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QApplication,QListWidget,QAbstractItemView,QTreeWidgetItem,\
                            QVBoxLayout,QDialog,QHBoxLayout,QLabel,QLineEdit,QPushButton,QComboBox

from PyQt5.QtGui import QDoubleValidator,QIntValidator
import copy

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

    def __init__(self, parent,variable_name,metadata):
        super(EditMetadata,self).__init__(parent)
        self.metadata=metadata
        Vlayout = QVBoxLayout()

        for key in metadata.keys():
            Hlayout = QHBoxLayout()
            Hlayout.addWidget(QLabel(key.replace('_','')))
            txt=metadata[key]
            if type(txt)==type(str()):
                ql=QLineEdit(txt)
            else:
                ql=QLineEdit(str(txt))
                ql.setValidator(QIntValidator())
            setattr(self, key, ql)
            Hlayout.addWidget(ql)
            Vlayout.addLayout(Hlayout)

        self.setLayout(Vlayout)
    
        self.center_window()
        self.setWindowTitle('Variable: %s' % variable_name)
    
    def exec(self):
        self.exec_()
        for key in self.metadata.keys():
            try:
                res=float(getattr(self, key).text())
            except:
                res=getattr(self, key).text()
            self.metadata[key]=res

        return self.metadata
    def center_window(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

