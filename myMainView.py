import os
import sys
import re

from PyQt5.QtCore import QPoint, QTimer
# from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QSpacerItem, QSizePolicy, QGridLayout, QPushButton

from calculate.readdata import read_las_file
from util.LSTMtarin import *
from faciestest.models import knnMOD, svmMOD, xgbMOD, RandomForestMOD, gbdtMOD
from util.DrillingOptimize import DrillingOptimize
from util.calculate_welllog import calculate_
from util.exportFileUtil import judge_file
from util.findSweetArea import findSweetArea
from util.lithofacies_prediction import LSTM_lithofacies_pred, joblib_lithofacies_pred
from util.readDataUtil import test_read_data, read_dialog_DP_param, read_dialog_sweetArea_param
from view.DPset_dialog import DialogWindow
from view.dialog_calculate_param import Dialog_calculate_param, read_dialog_calculate_param
from view.dialog_optimizeDrilling import Dialog_OptimizeDrilling, read_dialog_OptimizeDrilling_param
from view.dialog_productionForecast import Dialog_productionForecast, read_dialog_productionForecast_param
from view.sweetAreaSearch import sweetAreaSearchDialogWindow
from view.windows_ import *
from joblib import load
import torch

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


# record_lithofacies_prediction_data_demo = {
#     "训练模型": {
#         "funname": {
#             "index": "predecteData"
#         }
#     },  # 训练的模型
#     "岩相预测数据": {
#         "wellname": {
#             "index": "predecteData"
#         }
#     }  # 预测数据
# }


class myMainView(QMainWindow):
    # 视图序列表 每创建一个视图 添加对应视图index
    view_index_list = []
    dataAll = {
    }
    # 模型操作记录
    record_lithofacies_prediction_data = {
        "训练模型": {},  # 训练的模型
        "岩相预测数据": {}  # 预测数据
    }
    # icon文件路径
    icon_filePath = {
        "logo": "image/logo2.png",
        "dataTable": "image/dataTable.png",
        "dataView": "image/dataView.png",
        "well": "image/well.png",
        "welllog": "image/icon_welllog.png",
        "well3D": "image/icon_3D.png",
        "well2D": "image/icon_2D.png",
        "DPLearning": "image/DPLearning.png",
        "sweetAreaSearch": "image/sweetAreaSearch.png",
        "OptimizeDrilling": "image/OptimizeDrilling.png",
        "productionForecast": "image/productionForecast.png",
        "KNN": "",
        "SVM": "",
        "Boosting": "",
        "RandomForest": "",
        "XGBoost": "",
        "LSTMClassifier": "",
    }
    # 甜点区
    sweetArea_list = {}

    flag = 0
    sel_well_ = None

    def __init__(self):
        # self.dataAll = dataAll
        super(QMainWindow, self).__init__()

        self.setupUi()
        self.addRibbonBtn()
        self.setEvent()

    # 更新模型记录视窗
    def addItems(self, treeWidget, data):
        for key, value in data.items():
            top_item = QTreeWidgetItem([key])
            treeWidget.addTopLevelItem(top_item)
            self.addChildren(top_item, value)

    def addChildren(self, parent, data):
        for key, value in data.items():
            if not isinstance(key, str):
                key = str(key)
            child_item = QTreeWidgetItem([str(key)])
            child_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            parent.addChild(child_item)
            if isinstance(value, dict):
                self.addChildren(child_item, value)
            else:
                pass

    def showContextMenu(self, pos):
        menu = QMenu(self.treeWidget_model)
        add_action = QAction("保存文件", self.treeWidget_model)
        # remove_action = QAction("Remove", self.treeWidget_model)

        menu.addAction(add_action)
        # menu.addAction(remove_action)
        selected_items = self.treeWidget_model.selectedItems()
        item_, parent_item_, parent_parent_item_ = None, None, None
        for item in selected_items:
            parent_item = item.parent()
            item_ = item.text(0)
            print(item.text(0))
            if parent_item:
                parent_item_ = parent_item.text(0)
                print("Selected item:", item.text(0))
                print("Parent item:", parent_item.text(0))
                parent_parent_item = parent_item.parent()
                if parent_parent_item:
                    parent_parent_item_ = parent_parent_item.text(0)
                    print("parent_parent_item item:", parent_parent_item.text(0))

        action = menu.exec_(self.treeWidget_model.mapToGlobal(pos))
        if action == add_action:
            judge_file(self.record_lithofacies_prediction_data, item_, parent_item_, parent_parent_item_)
            print("Add action triggered")
        # elif action == remove_action:
        #     print("Remove action triggered")

    def update_record_model_operation(self):
        # 添加顶层项目
        if self.findChild(QTreeWidget, "treeWidget_model"):
            self.treeWidget_model.deleteLater()
        self.treeWidget_model = QtWidgets.QTreeWidget()
        self.treeWidget_model.setHeaderHidden(True)
        # 连接右键菜单事件
        self.treeWidget_model.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeWidget_model.customContextMenuRequested.connect(self.showContextMenu)
        # self.setContextMenuPolicy(Qt.DefaultContextMenu)

        self.vlay_record.addWidget(self.treeWidget_model)
        self.treeWidget_model.setGeometry(QtCore.QRect(180, 150, 256, 192))
        self.treeWidget_model.setObjectName("treeWidget_model")
        self.treeWidget_model.headerItem().setText(0, " ")
        if self.record_lithofacies_prediction_data["训练模型"]:
            top_item = QTreeWidgetItem(["训练模型"])
            top_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)

            self.treeWidget_model.addTopLevelItem(top_item)
            self.addChildren(top_item, self.record_lithofacies_prediction_data["训练模型"])

        # 岩相预测数据
        if self.record_lithofacies_prediction_data["岩相预测数据"]:
            top_item = QTreeWidgetItem(["岩相预测数据"])
            top_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)

            self.treeWidget_model.addTopLevelItem(top_item)
            self.addChildren(top_item, self.record_lithofacies_prediction_data["岩相预测数据"])

    # 模型记录视窗
    def record_model_operation(self):
        if self.findChild(QDockWidget, "modelOperation"):
            return
        dock = QtWidgets.QDockWidget("modelOperation")
        dock.setObjectName("modelOperation")
        # dock.setFeatures(dock.DockWidgetMovable)
        self.welldata.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)
        scroll = QtWidgets.QScrollArea()
        dock.setWidget(scroll)
        content = QtWidgets.QWidget()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        self.vlay_record = QtWidgets.QFormLayout(content)
        self.vlay_record.setContentsMargins(0, 0, 0, 0)

    def well2D_Btn_clicked(self, vt):
        if not self.findChild(CollapsibleBox, "wellheadData"):  # 未导入数据
            # 创建消息框
            msg_box = QMessageBox()
            # 设置消息框标题和文本
            msg_box.setWindowTitle("提示")
            msg_box.setText("请导入井数据")
            self.show_message(message="请导入井数据", time=3)
            # 设置消息框图标和按钮
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setStandardButtons(QMessageBox.Ok)
            # 显示消息框并等待用户响应
            msg_box.exec_()
            return
        wellheads = []
        for key, value in self.dataAll.items():
            if "wellhead" in value:
                k = value["wellhead"]
                k.update({'well': key})
                wellheads.append(k)
        # wellheads = [value["wellhead"].update({'well': key}) for key, value in self.dataAll.items() if
        #              "wellhead" in value]
        if wellheads:
            wellheads = pd.DataFrame(wellheads)
            self.create_view_btn(vt, data=wellheads)

    def well3D_Btn_clicked(self, vt):
        if not self.findChild(CollapsibleBox, "wellheadData"):  # 未导入数据
            # 创建消息框
            msg_box = QMessageBox()
            # 设置消息框标题和文本
            msg_box.setWindowTitle("提示")
            msg_box.setText("请导入井数据")
            self.show_message(message="请导入井数据", time=3)

            # 设置消息框图标和按钮
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setStandardButtons(QMessageBox.Ok)
            # 显示消息框并等待用户响应
            msg_box.exec_()
            return

        wellheads = []
        for key, value in self.dataAll.items():
            if "wellhead" in value:
                k = value["wellhead"]
                k.update({'well': key})
                wellheads.append(k)
        if wellheads:
            wellheads = pd.DataFrame(wellheads)
            print(wellheads)
            self.create_view_btn(vt, data=wellheads)

    def show_message(self, message, time=None):
        self.statusbar.showMessage(message)
        if time:
            self.timer.start(time * 1000)  # 3000毫秒即3秒

    def clearStatusBar(self):
        # 隐藏状态栏消息
        self.statusBar().clearMessage()
        self.timer.stop()
        self.show_message(message="Ready")

    ##功能按钮创建
    def addRibbonBtn(self):
        # 2D井位图
        self.well2D = QToolButton()
        self.well2D.setObjectName("well2D")
        self.well2D.setText("well2D")
        self.well2D.setIcon(
            QIcon(self.icon_filePath[self.well2D.objectName()]))  # Replace "icon.png" with your icon file path
        self.well2D.setIconSize(QSize(48, 48))
        self.well2D.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        # 方法1 通过QStackedLayout布局实现多页面切换
        self.well2D.clicked.connect(lambda: self.well2D_Btn_clicked(self.well2D.objectName()))
        self.ribbon_layout.addWidget(self.well2D)

        # 3D井位图
        self.well3D = QToolButton()
        self.well3D.setObjectName("well3D")
        self.well3D.setText("well3D")
        self.well3D.setIcon(
            QIcon(self.icon_filePath[self.well3D.objectName()]))  # Replace "icon.png" with your icon file path
        self.well3D.setIconSize(QSize(48, 48))
        self.well3D.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        # 方法1 通过QStackedLayout布局实现多页面切换
        self.well3D.clicked.connect(lambda: self.well3D_Btn_clicked(self.well3D.objectName()))
        self.ribbon_layout.addWidget(self.well3D)

        # 测井图
        self.welllog = QToolButton()
        self.welllog.setObjectName("welllog")
        self.welllog.setText("测井曲线")
        self.welllog.setIcon(
            QIcon(self.icon_filePath[self.welllog.objectName()]))  # Replace "icon.png" with your icon file path
        self.welllog.setIconSize(QSize(48, 48))
        self.welllog.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        # 方法1 通过QStackedLayout布局实现多页面切换
        # self.welllog.clicked.connect(lambda: self.init_calculateParam_dialog(self.welllog.objectName()))
        self.welllog.clicked.connect(self.show_calculateParam_dialog)

        self.ribbon_layout.addWidget(self.welllog)

        # 模型训练
        self.DPLearning = QToolButton()
        self.DPLearning.setObjectName("DPLearning")
        self.DPLearning.setText("深度学习")
        self.DPLearning.setIcon(
            QIcon(self.icon_filePath[self.DPLearning.objectName()]))  # Replace "icon.png" with your icon file path
        self.DPLearning.setIconSize(QSize(48, 48))
        self.DPLearning.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        # 方法1 通过QStackedLayout布局实现多页面切换
        self.DPLearning.clicked.connect(self.show_DPset_dialog)
        self.ribbon_layout.addWidget(self.DPLearning)

        # 甜点区搜索
        self.DPLearning = QToolButton()
        self.DPLearning.setObjectName("sweetAreaSearch")
        self.DPLearning.setText("甜点区搜索")
        self.DPLearning.setIcon(
            QIcon(self.icon_filePath[self.DPLearning.objectName()]))  # Replace "icon.png" with your icon file path
        self.DPLearning.setIconSize(QSize(48, 48))
        self.DPLearning.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        # 方法1 通过QStackedLayout布局实现多页面切换
        self.DPLearning.clicked.connect(self.show_sweetAreaSearch_dialog)
        self.ribbon_layout.addWidget(self.DPLearning)

        # 钻井参数优化
        self.DPLearning = QToolButton()
        self.DPLearning.setObjectName("OptimizeDrilling")
        self.DPLearning.setText("钻井参数优化")
        self.DPLearning.setIcon(
            QIcon(self.icon_filePath[self.DPLearning.objectName()]))  # Replace "icon.png" with your icon file path
        self.DPLearning.setIconSize(QSize(48, 48))
        self.DPLearning.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        # 方法1 通过QStackedLayout布局实现多页面切换
        self.DPLearning.clicked.connect(self.show_OptimizeDrilling_dialog)
        self.ribbon_layout.addWidget(self.DPLearning)

        # 产量预测
        self.productionForecast = QToolButton()
        self.productionForecast.setObjectName("productionForecast")
        self.productionForecast.setText("产量预测")
        self.productionForecast.setIcon(
            QIcon(self.icon_filePath[
                      self.productionForecast.objectName()]))  # Replace "icon.png" with your icon file path
        self.productionForecast.setIconSize(QSize(48, 48))
        self.productionForecast.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        # 方法1 通过QStackedLayout布局实现多页面切换
        self.productionForecast.clicked.connect(self.show_productionForecast_dialog)
        self.ribbon_layout.addWidget(self.productionForecast)

        self.ribbon_layout.addStretch()

    def show_productionForecast_dialog(self):
        dialog = Dialog_productionForecast(self)
        dialog.show()
        if dialog.exec_():
            productionForecast_param = read_dialog_productionForecast_param(dialog)
            print(productionForecast_param)
            window = windows_ProductionForcast()
            window.map(productionForecast_param)
            self.view_zone_layout.addWidget(window)
            self.create_view_btn(productionForecast_param["well_name"] + "产量预测", notaddview=True)

    # 岩相预测模型选择视窗
    def show_DPset_dialog(self):
        dialog = DialogWindow(self)
        dialog.show()
        if dialog.exec_():
            self.record_model_operation()
            DP_param = read_dialog_DP_param(dialog)
            if DP_param["custom_training_model"]:
                filepath = DP_param["data_filePath"]
                data = test_read_data(filepath)
                print(data.columns)
                # sel_train_list = ['GR', 'SP.MV', 'CAL.', 'AC.', 'CNL.V/V', 'LLD', 'LLS.OHMM']
                # logs = ['GR', 'SP.MV', 'CAL.', 'AC.', 'CNL.V/V', 'DEN.', 'LLD', 'LLS.OHMM']
                sel_train_list = ['GR', 'SP', 'CAL', 'AC', 'CNL', 'LLD', 'LLS']
                logs = ['GR', 'SP', 'CAL', 'AC', 'CNL', 'DEN', 'LLD', 'LLS']
                x_train = data[sel_train_list].values
                y_train = data['FACIES']
                model_fun = {
                    "KNN": knnMOD,
                    "SVM": svmMOD,
                    "Boosting": gbdtMOD,
                    "RandomForest": RandomForestMOD,
                    "XGBoost": xgbMOD,
                    "LSTMClassifier": LSTM_classifier
                }
                # 训练结果
                if DP_param["model"] == "XGBoost":
                    pipe = model_fun[DP_param["model"]](x_train, y_train - 1, DP_param['model_param'])
                    y_pred = pipe.predict(x_train) + 1
                elif DP_param["model"] == "LSTMClassifier":
                    y_pred, pipe = model_fun[DP_param["model"]](data, DP_param['model_param'], sel_train_list)
                    logs = data.columns[1:]
                else:
                    pipe = model_fun[DP_param["model"]](x_train, y_train, DP_param['model_param'])
                    y_pred = pipe.predict(x_train)

                # 保存模型
                if DP_param["model"] not in self.record_lithofacies_prediction_data["训练模型"]:
                    self.record_lithofacies_prediction_data["训练模型"].update(
                        {DP_param["model"]: {DP_param["DefaultModelName"]: pipe}})  # 记录预测数据
                else:
                    self.record_lithofacies_prediction_data["训练模型"][DP_param["model"]].update(
                        {DP_param["DefaultModelName"]: pipe})
                # 添加视图按钮
                """
                在sel_view_zone 创建按钮
                在stackedLayout添加视图
                view_index_list记录视图id
                """
                self.create_view_btn(DP_param["model"], data=data, y_pred=y_pred, facies=data['FACIES'],
                                     logs=logs, anlays=True)
                self.create_view_btn(DP_param["model"], data=data, y_pred=y_pred, facies=data['FACIES'],
                                     logs=logs)

            else:
                viewType = DP_param["sel_well"]
                data = self.dataAll[viewType]['welllog']
                model_file_path = DP_param["model"]
                model_name, file_type = model_file_path.split("/")[-1].split(".")  # 获取文件类型
                print(model_file_path)
                if file_type == 'pt':
                    model = torch.load(model_file_path)  # 加载模型
                    print(data.columns)
                    data, y_pred, logs = LSTM_lithofacies_pred(data=data, model=model)
                else:
                    model = load(model_file_path)
                    data, y_pred, logs = joblib_lithofacies_pred(data=data, model=model)

                if viewType in self.record_lithofacies_prediction_data["岩相预测数据"]:
                    key = str(len(self.record_lithofacies_prediction_data["岩相预测数据"][viewType]))
                    self.record_lithofacies_prediction_data["岩相预测数据"][viewType].update(
                        {key: y_pred})  # 记录预测数据
                else:
                    self.record_lithofacies_prediction_data["岩相预测数据"].update(
                        {viewType: {'0': y_pred}})  # 记录预测数据
                self.create_view_btn(viewType=viewType, data=data, y_pred=y_pred, facies=data['FACIES'],
                                     logs=logs, anlays=True, prediction=True)
                self.create_view_btn(viewType=viewType, data=data, y_pred=y_pred, facies=data['FACIES'],
                                     logs=logs, prediction=True)
                print(self.record_lithofacies_prediction_data["岩相预测数据"])
            # 向刷新的显示部件dock--modelOperation
            self.update_record_model_operation()

    def show_OptimizeDrilling_dialog(self):
        dialog = Dialog_OptimizeDrilling(self)
        dialog.show()
        if dialog.exec_():
            OptimizeDrilling_param = read_dialog_OptimizeDrilling_param(dialog)
            DrillingOptimize(param=OptimizeDrilling_param)

    def show_calculateParam_dialog(self):
        data, depth_col, welllogs = self.get_current_data()
        win = windows_welllog_new(data, depth_col, welllogs)
        self.view_zone_layout.addWidget(win)
        self.create_view_btn("welllog", notaddview=True)

        wellhead = self.findChild(CollapsibleBox, "wellheadData")
        welllogs_box = self.findChild(CollapsibleBox, "welllog")

        if not wellhead or not welllogs_box:  # 未导入数据
            # 创建消息框
            msg_box = QMessageBox()
            # 设置消息框标题和文本
            msg_box.setWindowTitle("提示")
            msg_box.setText("请导入井数据")
            self.show_message(message="请导入井数据", time=3)
            # 设置消息框图标和按钮
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setStandardButtons(QMessageBox.Ok)
            # 显示消息框并等待用户响应
            msg_box.exec_()
            return

        dialog = Dialog_calculate_param(self)
        dialog.show()
        if dialog.exec_():
            # self.record_model_operation()
            calculate_param = read_dialog_calculate_param(dialog)
            wellName = calculate_param['wellname']
            df = self.dataAll[wellName]['welllog']
            df, depth = calculate_(df)
            geo_params = ["POR", "VSH", "Sw", "PERM"]
            for well_curve_type in geo_params:
                # 读取测井数据类型
                well_curve_data = df[well_curve_type]  # 读取测井数据
                # 将字典添加到 self.dataAll 中
                self.dataAll[wellName]["welllog"].update({well_curve_type: well_curve_data})

            if not self.findChild(CollapsibleBox, "geoParam"):
                box = CollapsibleBox("测井计算参数")
                box.setObjectName('geoParam')
                self.vlay.addWidget(box)
                lay = QtWidgets.QVBoxLayout()
                for well in geo_params:
                    Qridio = QCheckBox(well)
                    Qridio.setObjectName(well)
                    Qridio.clicked.connect(self.click_well_data)
                    lay.addWidget(Qridio)
                box.setContentLayout(lay)

    def show_sweetAreaSearch_dialog(self):
        dialog = sweetAreaSearchDialogWindow(self)
        dialog.show()
        if dialog.exec_():
            # self.record_model_operation()
            sweetArea_param = read_dialog_sweetArea_param(dialog)
            heatmap_data, suitable_blocks_dict = findSweetArea(sweetArea_param)
            self.sweetArea_list = suitable_blocks_dict
            window = windows_sweetArea()
            window.heatmap(heatmap_data)
            self.view_zone_layout.addWidget(window)
            self.create_view_btn("sweetAreaHeatMap", notaddview=True)

            # self.worker_thread = Thread_creat_view(data=heatmap_data)
            # # self.worker_thread.finished.connect(
            # #     lambda: self.sweetAreaSearch_view_btn(sweetArea_param, suitable_blocks_dict))  # 连接工作线程的信号
            # self.worker_thread.window_created.connect(self.add_window_to_layout)
            # self.worker_thread.start()

            # 钻井参数优化
            # DrillingOptimize(param=sweetArea_param, data=suitable_blocks_dict)

    def sweetAreaSearch_view_btn(self, sweetArea_param, suitable_blocks_dict):
        DrillingOptimize(param=sweetArea_param, data=suitable_blocks_dict)

    def add_window_to_layout(self, window):
        # 将窗口添加到布局中
        print(window)
        self.view_zone_layout.addWidget(window)
        print("ok")
        self.create_view_btn("sweetAreaHeatMap", notaddview=True)

    def workerFinished(self):
        # self.label.setText("Worker Status: Finished")
        print("Worker Status: Finished")
        self.workerThread1.start()

    def setupUi(self):
        self.setMinimumSize(900, 600)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(self.icon_filePath['logo']), QtGui.QIcon.Mode.Normal,
                       QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)
        self.main_widget = QWidget(self)
        self.main_widget.setStyleSheet('QWidget{background-color: gray};}')
        self.main_layout = QGridLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_widget.setLayout(self.main_layout)
        # 功能区
        self.ribbon = QWidget()
        self.ribbon.setFixedHeight(100)
        # self.ribbon.setStyleSheet("border: 2px solid red;background-color: #FFFFFF")
        self.ribbon.setStyleSheet("background-color: #FFFFFF")
        self.main_layout.addWidget(self.ribbon, 0, 0, 1, 2)
        # 功能区设置
        self.ribbon_layout = QHBoxLayout()
        self.ribbon.setLayout(self.ribbon_layout)
        self.main_layout.addWidget(self.ribbon, 0, 0, 1, 2)

        # well数据区
        self.welldata = QMainWindow()
        self.welldata.setFixedWidth(250)
        self.welldata.setStyleSheet("background-color: #FFFFFF};")
        dock = QtWidgets.QDockWidget("Input")
        dock.setFeatures(dock.DockWidgetMovable)
        self.welldata.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)
        scroll = QtWidgets.QScrollArea()
        dock.setWidget(scroll)
        content = QtWidgets.QWidget()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        self.vlay = QtWidgets.QFormLayout(content)
        self.vlay.setContentsMargins(0, 0, 0, 0)

        self.main_layout.addWidget(self.welldata, 1, 0, 2, 1)

        # 视图选择区

        self.sel_view_main = QWidget()
        self.sel_view_main_layout = QHBoxLayout(self.sel_view_main)
        self.sel_view_main_layout.setContentsMargins(0, 0, 0, 0)

        self.sel_view = QWidget()
        self.sel_view.setFixedHeight(25)
        self.sel_view.setObjectName("sel_view")
        self.sel_View_layout = QHBoxLayout()
        self.sel_View_layout.setSizeConstraint(QLayout.SetFixedSize)
        self.sel_View_layout.setSpacing(0)
        self.sel_View_layout.setContentsMargins(0, 0, 0, 0)
        self.sel_view.setLayout(self.sel_View_layout)

        # scroll = QScrollArea()  # 滚动区 域
        # scroll.setWidget(self.sel_view)  # 监控sel_view
        # self.sel_view_main_layout.addWidget(scroll)

        self.sel_view_main_layout.addWidget(self.sel_view)
        self.main_layout.addWidget(self.sel_view_main, 1, 1, 1, 1)
        # 视图显示区
        self.view_zone = QWidget()
        self.view_zone_layout = QStackedLayout()
        self.view_zone_layout.setContentsMargins(0, 0, 0, 0)
        self.view_zone.setLayout(self.view_zone_layout)
        self.main_layout.addWidget(self.view_zone, 2, 1, 1, 1)

        # 中心视图
        self.setCentralWidget(self.main_widget)
        self.menubar = QtWidgets.QMenuBar()
        self.menubar.setGeometry(QtCore.QRect(0, 0, 885, 21))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(parent=self.menubar)
        self.menu.setEnabled(True)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(parent=self.menubar)
        self.menu_2.setObjectName("menu_2")
        self.menu_3 = QtWidgets.QMenu(parent=self.menubar)
        self.menu_3.setEnabled(True)
        self.menu_3.setObjectName("menu_3")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar()
        self.statusbar.showMessage("Ready")
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        # 设置计时器以在三秒后隐藏状态栏消息
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.clearStatusBar)

        self.action = QtWidgets.QAction()
        self.action.setCheckable(False)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(self.icon_filePath['dataTable']), QtGui.QIcon.Mode.Normal,
                        QtGui.QIcon.State.Off)
        self.action.setIcon(icon1)
        self.action.setObjectName("action")
        self.action_2 = QtWidgets.QAction()
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(self.icon_filePath['dataView']), QtGui.QIcon.Mode.Normal,
                        QtGui.QIcon.State.Off)
        self.action_2.setIcon(icon2)
        self.action_2.setObjectName("action_2")
        self.action_3 = QtWidgets.QAction()
        self.action_3.setObjectName("action_3")
        self.action1 = QtWidgets.QAction()

        self.action1.setObjectName("action1")
        self.importWelllog = QtWidgets.QAction()

        self.importWelllog.setObjectName("importWelllog")
        self.importWellhead = QtWidgets.QAction()
        self.importWellhead.setObjectName("importWellhead")
        self.menu.addAction(self.importWelllog)
        self.menu.addAction(self.importWellhead)
        self.menu_2.addAction(self.action)
        self.menu_2.addAction(self.action_2)
        self.menu_3.addAction(self.action_3)
        self.menu_3.addAction(self.action1)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())
        self.menubar.addAction(self.menu_3.menuAction())
        self.retranslateUi(self)

    def menuActionClicked(self):
        # 获取触发了菜单项的动作
        self.findChild(QPushButton, "sel_btn_" + re.sub("action_", "", self.sender().objectName())).click()
        # print('菜单项 "{}" 被点击了！'.format(action.text()))

    def showMenu(self):
        "将已经记录的 视图创建action"

        # 创建菜单menu：
        selview_menu = QMenu(self)
        selview_menu.setObjectName("selview_menu")
        for vt in self.view_index_list:
            # 创建一个新的菜单项
            new_action = QAction(vt, self)
            # 连接菜单项的触发信号到槽函数
            new_action.setObjectName("action_" + vt)
            new_action.triggered.connect(self.menuActionClicked)
            # 将菜单项添加到菜单中
            selview_menu.addAction(new_action)
        # 计算菜单显示的位置
        menu_width = selview_menu.sizeHint().width()
        button_pos = self.menu_button.mapToGlobal(self.menu_button.rect().bottomRight())
        lac = QPoint(button_pos.x() - menu_width, button_pos.y())
        # 显示菜单
        selview_menu.exec_(lac)

    def create_sel_view_menu(self):
        # 创建一个按钮
        self.menu_button = QPushButton("▼")
        self.menu_button.setStyleSheet("background-color:#43508b;")
        self.menu_button.setFixedSize(40, 30)
        self.menu_button.clicked.connect(self.showMenu)
        # 在水平布局中添加伸缩器，将按钮推到右边
        self.sel_view_main_layout.addStretch()
        self.sel_view_main_layout.addWidget(self.menu_button)

    def create_view_btn(self, viewType, data=None, y_pred=None, facies=None, logs=None, anlays=None, prediction=None,
                        notaddview=None):
        """
        创建视图及视图选择按钮
        :return:
        """
        if self.sender().objectName() != self.DPLearning.objectName() and viewType in self.view_index_list:
            print("已创建")
            return
        elif anlays and viewType + "-LCAM" in self.view_index_list:
            print("已创建")
            return
        elif not anlays and any(viewType + "-" + string in self.view_index_list for string in ["LSM", "LPM"]):
            print("已创建")
            return

        if len(self.view_index_list) == 0:
            self.create_sel_view_menu()

        # #创建视窗
        viewname = None
        if not notaddview:
            viewname = self.push_view(viewType, data, y_pred, facies, logs, anlays, prediction=prediction)
        # 添加视图切换按钮
        if viewname:
            for ivn in viewname:
                vt = viewType + "-" + ivn
                self.view_index_list.append(vt)
                # 设置当前显示视图
                self.view_zone_layout.setCurrentIndex(self.view_index_list.index(vt))
                self.push_btn(vt)
        else:
            self.view_index_list.append(viewType)
            self.view_zone_layout.setCurrentIndex(self.view_index_list.index(viewType))
            self.push_btn(viewType)
        # sel_btn = QWidget(parent=self.sel_view)
        # custom_button = CustomButton(self.icon_filePath[viewType], viewType, sel_btn)
        # # layout = QHBoxLayout()
        # # layout.addWidget(custom_button)
        # sel_btn.setFixedSize(80, 20)
        # sel_btn = QPushButton(parent=self.sel_view)
        # sel_btn.setIcon(QtGui.QIcon(self.icon_filePath[viewType]))
        # sel_btn.clicked.connect(lambda: self.change_view(viewType))
        # sel_btn.setFixedSize(80, 20)
        # self.sel_View_layout.addWidget(sel_btn)
        # for i in range(self.sel_View_layout.count()):
        #     self.sel_View_layout.setStretch(i, 0)
        # self.sel_View_layout.addStretch(2)
        # self.sel_view
        pass

    def push_btn(self, viewType):
        # 创建按钮
        sel_btn = QPushButton()
        # 设置按钮唯一标识名
        sel_btn.setObjectName("sel_btn_" + viewType)

        sel_btn.setLayout(QHBoxLayout())
        sel_btn.layout().setContentsMargins(0, 0, 0, 0)
        sel_btn.clicked.connect(lambda: self.change_view(viewType))
        # 添加左边图标
        icon_label = QLabel()
        size_ = QSize(20, 20)
        icon_label.setFixedSize(size_)
        if viewType.split('-')[0] in self.icon_filePath:
            icon_label.setPixmap(QIcon(self.icon_filePath[viewType.split('-')[0]]).pixmap(size_))
        sel_btn.layout().addWidget(icon_label)
        # 添加中间文本
        text_label = QLabel(viewType)
        sel_btn.layout().addWidget(text_label, alignment=Qt.AlignCenter)
        sel_btn.layout().addStretch()
        # 创建内部按钮
        inner_button = QPushButton("x")
        inner_button.setFixedSize(20, 20)
        inner_button.setStyleSheet("")
        inner_button.clicked.connect(lambda: self.close_view(viewType))
        # 将内部按钮添加到主按钮的部件中
        sel_btn.layout().addWidget(inner_button)
        # 创建按键后 自动触发
        sel_btn.click()
        # 将主按钮添加到布局中
        sel_btn.setFixedSize(150, 30)  # 设置初始显示大小为（300，40）
        sel_btn.setMaximumWidth(200)
        sel_btn.setFixedHeight(30)
        # sel_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.sel_View_layout.addWidget(sel_btn)

    def close_view(self, viewType):
        self.sel_view.findChild(QPushButton, "sel_btn_" + viewType).deleteLater()
        self.view_zone_layout.takeAt(self.view_index_list.index(viewType)).widget().deleteLater()
        self.view_index_list.remove(viewType)
        if len(self.view_index_list) == 0:
            # 关闭全部视图，视图按键删除
            self.menu_button.deleteLater()

    def push_view(self, viewType, data=None, y_pred=None, facies=None, logs=None, anlays=None, prediction=None):
        # 创建视图
        if viewType == 'well3D':
            win = windows_wellhead_3D(data)
            self.view_zone_layout.addWidget(win)
        elif viewType == 'well2D':
            win = windows_wellhead_2D(data)
            self.view_zone_layout.addWidget(win)
        elif viewType == 'welllog':
            win = windows_welllog()
            self.view_zone_layout.addWidget(win)
        else:
            viewname = []
            if not anlays:
                # 绘制深度学习结果视图
                win2 = windows_KNN()
                viewname.append(win2.drawLPM(data, y_pred, facies, logs, prediction=prediction))
                self.view_zone_layout.addWidget(win2)
                win1 = windows_KNN()
                viewname.append(win1.drawLSM(y_pred))
                self.view_zone_layout.addWidget(win1)

            else:
                win = windows_KNN()
                viewname.append(win.drawLCAM(data, y_pred))
                self.view_zone_layout.addWidget(win)
            return viewname
        return None

    def change_btn_color(self, viewType):
        sender_button = self.sender()
        # 设置所有按钮的默认样式
        for child_ in self.sel_view.children():
            if "sel_btn_" in child_.objectName():
                child_.setStyleSheet('background-color:white;')
        # 设置当前按钮的选中样式
        sender_button.setStyleSheet('background-color: #F6B000; color: white;')

    def change_view(self, viewType):
        """
        根据点击按钮对应的视图名称 切换视图
        :param viewType:
        :return:
        """
        self.view_zone_layout.setCurrentIndex(self.view_index_list.index(viewType))
        self.change_btn_color(viewType)

    def setEvent(self):
        self.importWellhead.triggered.connect(self.Select_wellhead_files)
        self.importWelllog.triggered.connect(self.Select_welllog_files)

    def set_sel_well(self):
        self.sel_well_ = self.sender().objectName()

    def get_current_data(self):
        # 更新well log视图
        # 获取当前选择井 及 选择的测井曲线数据
        data, depth_col, welllogs = [], None, []
        wellhead = self.findChild(CollapsibleBox, "wellheadData")
        welllogs_box = self.findChild(CollapsibleBox, "welllog")
        # 查找 CollapsibleBox 中选中的 QRadioButton
        if not wellhead or not welllogs_box:  # 未导入数据
            # self.create_view_btn(self.welllog.objectName())  # 创建空白视图
            return data, depth_col, welllogs
        for child_widget in wellhead.findChildren(QRadioButton):
            if child_widget.isChecked():
                # 在这里处理选中的 QRadioButton
                well = child_widget.text()  # 选择井
                print(well)
                welllogs = []  # 选择测井曲线
                # 查找 CollapsibleBox 中选中的 QCheckBox
                for child_widget in welllogs_box.findChildren(QCheckBox):
                    if child_widget.isChecked():
                        welllogs.append(child_widget.text())
                # 查找 CollapsibleBox 中选中的 QCheckBox
                if self.findChild(CollapsibleBox, "geoParam"):
                    geo_param_box = self.findChild(CollapsibleBox, "geoParam")
                    for child_widget in geo_param_box.findChildren(QCheckBox):
                        if child_widget.isChecked():
                            welllogs.append(child_widget.text())
                depth_col = 'DEPT'
                if depth_col not in welllogs:
                    welllogs.append(depth_col)
                data = self.dataAll[well]['welllog'][welllogs]
                welllogs.remove(depth_col)

                return data, depth_col, welllogs
        return data, depth_col, welllogs

    def click_well_data(self):
        # 先判断当前显示视窗是否为测井曲线图、
        if "welllog" in self.view_index_list:
            if self.view_zone_layout.currentIndex() == self.view_index_list.index("welllog"):
                data, depth_col, welllogs = self.get_current_data()
                # 删除w原来wellog视图 重新绘制
                win = windows_welllog_new(data, depth_col, welllogs)
                self.close_view("welllog")
                self.view_zone_layout.addWidget(win)
                self.create_view_btn("welllog", notaddview=True)

    def Select_wellhead_files(self):
        init_path = "D:/File/24石工大赛/data/1_井位"
        file_paths, _ = QFileDialog.getOpenFileNames(self, "选择文件", init_path,
                                                     "Excel文件 (*.xlsx *xls);;文本文件 (*.txt);;Word文件 (*.docx);;All (*.)")
        if file_paths:
            file_path = file_paths[0]
            file_type = os.path.basename(file_path).split('.')[1]
            if file_type == "xlsx" or file_type == "xls":
                data = pd.read_excel(file_path)
                # 将字典转换为 DataFrame
                wellhead_df = pd.DataFrame(data)
                wellhead_df.set_index('wellname', inplace=True)
                # 将 DataFrame 转换为字典
                wellhead_dict = wellhead_df.T.to_dict()
                # 将字典添加到 self.dataAll 中
                for well_name, value in wellhead_dict.items():
                    if well_name not in self.dataAll:
                        self.dataAll[well_name] = {}
                    self.dataAll[well_name].update({"wellhead": value})
            else:
                pass

            # 重置well数据
            find_wellheadDate = self.findChild(QWidget, 'wellheadData')
            if find_wellheadDate:
                find_wellheadDate.deleteLater()

            box = CollapsibleBox("well")
            box.setObjectName('wellheadData')
            self.vlay.addWidget(box)
            lay = QtWidgets.QVBoxLayout()
            for well in self.dataAll:
                Qridio = QRadioButton(well)
                Qridio.setObjectName(well)
                Qridio.clicked.connect(self.set_sel_well)
                Qridio.clicked.connect(self.click_well_data)
                lay.addWidget(Qridio)
            box.setContentLayout(lay)

    def Select_welllog_files(self):
        """
        导入测井数据
        :param self:
        :return:
        """
        init_path = "D:/File/24石工大赛/2024 CPEDC 方案设计类/las测井曲线"
        file_paths, _ = QFileDialog.getOpenFileNames(self, "选择文件", init_path,
                                                     "Well log(LAS) (*.las)")

        welllog = {}
        curve_type = []  # 记录测井数据类型
        # 遍历选择的文件路径，按文件名（井名）读取每口井的测井数据
        for i, fp in enumerate(file_paths):
            wellName = os.path.basename(fp).split('.')[0]
            # 读取测井数据类型
            well_curve_type, well_curve_data = read_las_file(fp)  # 读取测井数据
            # well_curve_data = well_curve_data.to_dict(orient='list')
            # 将字典添加到 self.dataAll 中
            if wellName not in self.dataAll:
                self.dataAll[wellName] = {}
            self.dataAll[wellName].update({"welllog": well_curve_data})
            # 记录全部的测井曲线类型
            curve_type = list(set(curve_type + well_curve_type))

        if file_paths:
            box = CollapsibleBox("well logs")
            box.setObjectName('welllog')
            self.vlay.addWidget(box)
            lay = QtWidgets.QVBoxLayout()
            for curve in curve_type:
                Qridio = QCheckBox(curve)
                # Qridio.setObjectName()
                Qridio.clicked.connect(self.click_well_data)
                lay.addWidget(Qridio)
            box.setContentLayout(lay)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "深度学习产量预测"))
        self.menu.setTitle(_translate("MainWindow", "数据导入"))
        self.menu_2.setTitle(_translate("MainWindow", "导出数据"))
        self.menu_3.setTitle(_translate("MainWindow", "帮助"))
        self.action.setText(_translate("MainWindow", "导出产量数据表格"))
        self.action_2.setText(_translate("MainWindow", "导出图表"))
        self.action_3.setText(_translate("MainWindow", "帮助"))
        self.action1.setText(_translate("MainWindow", "关于"))
        self.importWelllog.setText(_translate("MainWindow", "测井数据"))
        self.importWellhead.setText(_translate("MainWindow", "井位"))


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


def draw_well_2D(layout, filePath):
    """
    绘制3D井位图
    :param layout:
    :return:
    """
    # print(draw_well_2D.__name__)
    # 创建布局
    # 调用绘图函数并将图像嵌入到 PyQt 窗体中
    # print(layout.count())
    remove_widget(layout)
    df = pd.read_excel(filePath)
    fig = figWellhead(df)
    canvas = FigureCanvas(fig)
    layout.addWidget(canvas)


def figWellhead(df):
    from adjustText import adjust_text
    import matplotlib.pyplot as plt
    # 假设你已经读取了数据
    # df = pd.read_excel("data.xlsx")

    # 创建图形
    fig = plt.figure(figsize=(6, 8))
    plt.scatter(df['井口坐标x'], df['井口坐标y'])

    # 创建一个空的文本列表
    texts = []

    # 在每个井位上添加井号到文本列表
    for i, txt in enumerate(df['井号']):
        texts.append(plt.text(df['井口坐标x'][i], df['井口坐标y'][i], txt))

    # 调整文本标签的位置以减少重叠
    adjust_text(texts)
    plt.rcParams["font.sans-serif"] = "SimHei"
    plt.rcParams["axes.unicode_minus"] = False
    # 设置标题和标签
    plt.title('井位坐标可视化')
    plt.xlabel('井口坐标x')
    plt.ylabel('井口坐标y')

    # 限制x和y轴的范围
    plt.xlim([0, 7000])
    plt.ylim([0, 10000])

    # 显示图形
    # plt.show()
    return fig


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = myMainView()
    print(window.dataAll)
    window.show()
    sys.exit(app.exec())
