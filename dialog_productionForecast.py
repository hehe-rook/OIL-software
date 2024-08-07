import sys
import re

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QToolButton, QDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon


class Dialog_productionForecast(QDialog):
    load_import_training_model = None

    # import_lithofacies_data_filePath = None

    def __init__(self, parent=None):
        super().__init__(parent)

        loadUi("view/_Dialog_ProductionForecast.ui", self)  # Load the UI file

        self.setWindowTitle("参量优化")
        self.btn_sel_well.clicked.connect(self.import_sel_well_)

    def import_sel_well_(self):
        print(self.parent().sel_well_)
        self.well_nm.setText(self.parent().sel_well_)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.toolButton = QToolButton()
        self.toolButton.setText("Open Dialog")
        self.toolButton.setIcon(QIcon("icon.png"))  # Replace "icon.png" with your icon file path
        self.toolButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolButton.clicked.connect(self.openDialog)
        layout.addWidget(self.toolButton)
        self.setLayout(layout)
        self.setWindowTitle("ToolButton with Icon and Text")
        self.show()

    def openDialog(self):
        dialog = Dialog_productionForecast()
        # dialog.dataReady.connect(lambda:self.DP_param(d))  # 连接数据准备就绪信号与槽函数
        if dialog.exec_():
            print(read_dialog_productionForecast_param(dialog))


def read_dialog_productionForecast_param(dialog_):
    OptimizeDrilling_param_ = {
        "well_name": dialog_.well_nm.text(),
        "well_nm": re.findall(r'\d+(?:\.\d+)?', dialog_.well_nm.text())[0],
        "liquid": dialog_.radioButton_Oil_BBL.text() if dialog_.radioButton_Oil_BBL.isChecked() else dialog_.radioButton_Gas_MCF.text(),
        "qi_min": dialog_.qi_min.value(),
        "qi_max": dialog_.qi_max.value(),
        "b_min": dialog_.b_min.value(),
        "b_max": dialog_.b_max.value(),
        "di_min": dialog_.di_min.value(),
        "di_max": dialog_.di_max.value(),
        "sigma_fit": dialog_.sigma_fit.value(),
        "sigma_pred": dialog_.sigma_pred.value(),
        "pred_interval": dialog_.pred_interval.value(),
    }
    return OptimizeDrilling_param_


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
