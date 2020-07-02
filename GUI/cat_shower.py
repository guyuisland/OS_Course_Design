from shower import Ui_Dialog
from PyQt5.QtWidgets import QDialog
class cat_shower(QDialog,Ui_Dialog):
    def __init__(self,name,text):
        super().__init__()
        self.text.setText(text)
        self.setWindowTitle(name)
        self.show()
        self.exec_()