import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QToolButton, QDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon


class Dialog_OptimizeDrilling(QDialog):
    load_import_training_model = None

    # import_lithofacies_data_filePath = None

    def __init__(self, parent=None):
        super().__init__(parent)

        loadUi("view/_dialog_OptimizeDrilling.ui", self)  # Load the UI file

        interval_num = 1
        if parent.sweetArea_list:
            for idx in parent.sweetArea_list['min']:
                self.comboBox_perforated_interval.addItem(
                    f"射孔段{interval_num}({parent.sweetArea_list['min'][idx]}-{parent.sweetArea_list['max'][idx]})".format())
                interval_num += 1
        # self.setFixedSize(400, 430)
        self.setWindowTitle("钻井参数优化")


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
        dialog = Dialog_OptimizeDrilling()
        # dialog.dataReady.connect(lambda:self.DP_param(d))  # 连接数据准备就绪信号与槽函数
        if dialog.exec_():
            print(read_dialog_OptimizeDrilling_param(dialog))


def read_dialog_OptimizeDrilling_param(dialog_):
    print(dialog_.comboBox_perforated_interval.currentText())
    import re
    # 使用正则表达式匹配数字
    numbers = re.findall(r'\d+(?:\.\d+)?', dialog_.comboBox_perforated_interval.currentText())
    # 将匹配到的字符串转换为对应的数据类型
    numbers = [int(num) if '.' not in num else float(num) for num in numbers]
    OptimizeDrilling_param_ = {
        "Depth_min": numbers[1],
        "Depth_max": numbers[2],
        "WOB_min": dialog_.WOB_min.value(),
        "WOB_max": dialog_.WOB_max.value(),
        "WURF_RPM_min": dialog_.WURF_RPM_min.value(),
        "WURF_RPM_max": dialog_.WURF_RPM_max.value(),
    }
    return OptimizeDrilling_param_


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
