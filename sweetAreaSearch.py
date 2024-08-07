import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QToolButton, QDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon

from util.readDataUtil import read_dialog_sweetArea_param


class sweetAreaSearchDialogWindow(QDialog):
    load_import_training_model = None

    # import_lithofacies_data_filePath = None

    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("view/_sweetAreaSearch.ui", self)  # Load the UI file
        # self.setFixedSize(400, 430)
        self.setWindowTitle("sweetAreaSearch")


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
        dialog = sweetAreaSearchDialogWindow()
        # dialog.dataReady.connect(lambda:self.DP_param(d))  # 连接数据准备就绪信号与槽函数
        if dialog.exec_():
            print(read_dialog_sweetArea_param(dialog))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
