import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QToolButton, QDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon


class Dialog_calculate_param(QDialog):
    load_import_training_model = None

    # import_lithofacies_data_filePath = None

    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("view/_dialog_calculate_param.ui", self)  # Load the UI file
        self.setWindowTitle("地质参数计算")
        self.btn_sel_well.clicked.connect(self.import_sel_well_)

    # self.btn_sel_well.clicked.connect(self.import_sel_well_)

    def import_sel_well_(self):
        print(self.parent().sel_well_)
        self.lineEdit_sel_wellname.setText(self.parent().sel_well_)
