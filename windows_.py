from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from calculate import calcuswpor
from util import pltUtil
from util.findSweetArea import corr_heatmap
from util.pltUtil import remove_widget
from util.trainingResultViewUtil import Lithofacies_statistical_map, Lithofacies_prediction_map, \
    Log_correlation_analysis_map, productionForecast_map
from util.viewUtil import draw_well_2D
from util.wellhead import drawWellhead

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


class windows_KNN(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    def drawLSM(self, param):
        Lithofacies_statistical_map(self.layout, param)
        return "LSM"

    def drawLPM(self, data=None, y_pred=None, facies=None, logs=None, prediction=None):
        Lithofacies_prediction_map(self.layout, data, y_pred, facies, logs, prediction=prediction)
        return "LPM"

    def drawLCAM(self, data, y_pred):
        Log_correlation_analysis_map(self.layout, data, y_pred)
        return "LCAM"


class windows_sweetArea(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    def heatmap(self, data):
        corr_heatmap(self.layout, data)


class windows_ProductionForcast(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    def map(self, param):
        productionForecast_map(self.layout, param)


class windows_wellhead_2D(QWidget):
    def __init__(self, data):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # wellheadFilePath = 'test/data.xlsx'
        # draw_well_2D(self.layout, wellheadFilePath)
        draw_well_2D(self.layout, data)


class windows_wellhead_3D(QWidget):
    def __init__(self, data):
        super().__init__()
        # self.setStyleSheet("background-color:green;")
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        drawWellhead(self.layout, data)


class windows_welllog(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.emptyGrapg()

    def emptyGrapg(self):
        remove_widget(self.layout)
        # 创建布局
        # layout = QVBoxLayout(self.chartView)
        # 调用绘图函数并将图像嵌入到 PyQt 窗体中
        fig = plt.figure(figsize=(20, 15))
        canvas = FigureCanvas(fig)
        self.layout.addWidget(canvas)


class windows_welllog_new(QWidget):
    def __init__(self, data, depth_col, curve_cols):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        if not depth_col:  # 空数据
            self.emptyGrapg()
        else:
            pltUtil.well_log_curces(self.layout, data, depth_col, curve_cols)

    def emptyGrapg(self):
        remove_widget(self.layout)
        # 创建布局
        # layout = QVBoxLayout(self.chartView)
        # 调用绘图函数并将图像嵌入到 PyQt 窗体中
        fig = plt.figure(figsize=(20, 15))
        canvas = FigureCanvas(fig)
        self.layout.addWidget(canvas)


class CollapsibleBox(QtWidgets.QWidget):
    """
    下拉列表工具设置
    """

    def __init__(self, title="", parent=None, iswelldata=None):
        super(CollapsibleBox, self).__init__(parent)

        if not iswelldata:
            self.toggle_button = QtWidgets.QToolButton(
                text=title, checkable=True, checked=False
            )
        # self.toggle_button.addAction()
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(
            QtCore.Qt.ToolButtonTextBesideIcon
        )
        self.toggle_button.setArrowType(QtCore.Qt.RightArrow)
        self.toggle_button.pressed.connect(self.on_pressed)

        self.toggle_animation = QtCore.QParallelAnimationGroup(self)

        self.content_area = QtWidgets.QScrollArea(
            maximumHeight=0, minimumHeight=0
        )
        self.content_area.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        self.content_area.setFrameShape(QtWidgets.QFrame.NoFrame)

        lay = QtWidgets.QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.toggle_button)
        lay.addWidget(self.content_area)

        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self, b"minimumHeight")
        )
        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self, b"maximumHeight")
        )
        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self.content_area, b"maximumHeight")
        )

    @QtCore.pyqtSlot()
    def on_pressed(self):
        checked = self.toggle_button.isChecked()
        self.toggle_button.setArrowType(
            QtCore.Qt.DownArrow if not checked else QtCore.Qt.RightArrow
        )
        self.toggle_animation.setDirection(
            QtCore.QAbstractAnimation.Forward
            if not checked
            else QtCore.QAbstractAnimation.Backward
        )
        self.toggle_animation.start()

    def setContentLayout(self, layout):
        lay = self.content_area.layout()
        del lay
        self.content_area.setLayout(layout)
        collapsed_height = (
                self.sizeHint().height() - self.content_area.maximumHeight()
        )
        content_height = layout.sizeHint().height()
        for i in range(self.toggle_animation.animationCount()):
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(500)
            animation.setStartValue(collapsed_height)
            animation.setEndValue(collapsed_height + content_height)

        content_animation = self.toggle_animation.animationAt(
            self.toggle_animation.animationCount() - 1
        )
        content_animation.setDuration(500)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)


# 页面按钮
class CustomButton(QWidget):
    def __init__(self, icon_path, text, parent):
        super().__init__(parent=parent)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 添加左边图标
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(icon_path).pixmap(QSize(20, 20)))
        layout.addWidget(icon_label)

        # 添加中间文本
        text_label = QLabel(text)
        layout.addWidget(text_label, alignment=Qt.AlignCenter)

        # 添加右边关闭按钮
        close_button = QPushButton("×")
        close_button.setStyleSheet("background-color:transparent; border:none; font-weight:bold; color:red;")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)
