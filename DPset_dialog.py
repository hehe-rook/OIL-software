import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QToolButton, QDialog, QFileDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon

from util.readDataUtil import read_dialog_DP_param


class DialogWindow(QDialog):
    load_import_training_model = None

    # import_lithofacies_data_filePath = None

    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("view/_DPset_dialog.ui", self)  # Load the UI file
        # self.setFixedSize(400, 430)
        self.setWindowTitle("QPS Window")

        self.comboBox_model.currentIndexChanged.connect(self.handleComboBoxChange)
        self.custom_training_model.clicked.connect(self.model_operation_sel)
        self.import_training_model.clicked.connect(self.model_operation_sel)
        self.btn_sel_model.clicked.connect(self.openFile)
        self.btn_import_lithofacies_data.clicked.connect(self.import_lithofacies_data)
        self.btn_sel_well.clicked.connect(self.import_sel_well_)

        # 初始化page显示
        self.custom_training_model.click()  # 模型操作初始化 自定义
        self.groupBox_param_set.setTitle("模型训练参数设置-" + self.comboBox_model.currentText())  # 模型训练参数设置 初始化标题
        self.modeParamSet.setCurrentIndex(self.comboBox_model.currentIndex())  # 初始选择算法 KNN

    def import_sel_well_(self):
        print(self.parent().sel_well_)
        self.lineEdit_sel_wellname.setText(self.parent().sel_well_)

    def import_lithofacies_data(self):
        options = QFileDialog.Options()
        init_path = ""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Model", init_path, "Lithofacies Data (*.xlsx)",
                                                   options=options)
        self.import_lithofacies_data_filePath = file_path
        self.lineEdit_import_lithofacies_data.setText(file_path)

    def openFile(self):
        options = QFileDialog.Options()
        init_path = ""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", init_path,
                                                   "ModelFile (*.pt *.joblib)",
                                                   options=options)
        if file_path:
            self.lineEdit_sel_model.setText(file_path)

    def handleComboBoxChange(self, index):
        self.groupBox_param_set.setTitle("模型训练参数设置-" + self.comboBox_model.currentText())
        self.modeParamSet.setCurrentIndex(index)

    def model_operation_sel(self):
        sender = self.sender()  # 获取触发信号的发送者
        if sender.objectName() == "import_training_model":
            self.model_operation.setCurrentIndex(0)  # 切换到第一页
            self.groupBox_param_set.hide()
        elif sender.objectName() == "custom_training_model":
            self.model_operation.setCurrentIndex(1)  # 切换到第二页
            self.groupBox_param_set.show()
