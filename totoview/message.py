

from PyQt5.QtWidgets import QMessageBox,QFileDialog

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

def get_file(parent,ext):
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    filenames, _ = QFileDialog.getOpenFileNames(parent,"QFileDialog.getOpenFileName()", "",ext, options=options)
    if not filenames:
         return
    else:
        return filenames