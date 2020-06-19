

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
    if not filenames:
         return
    else:
        return filenames

def put_file(parent,ext,exs):
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    filenames, _ = QFileDialog.getSaveFileName(parent,"QFileDialog.getSaveFileName()", "",ext, options=options)
    if not filenames:
         return
    else:
        if not filenames.endswith(exs):
            filenames+=exs
        return filenames