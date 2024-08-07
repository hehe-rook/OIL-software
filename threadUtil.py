import sys
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class WorkerThread(QThread):
    # 定义信号，用于与主线程通信
    finished = pyqtSignal()
    # testSignal = pyqtSignal()
    drawViewSignal = pyqtSignal()

    def __init__(self, parent=None, message=None):
        super().__init__(parent)
        self.message = message
        print(self.message)

    def run(self):
        # 模拟耗时操作
        # for i in range(1, 11):
        #     print("Working...", self.message, i)
        #     self.testSignal.emit()
        #     self.sleep(1)
        # 执行绘图信号
        print("开始线程")
        self.drawViewSignal.emit()
        # self.sleep(1)
        # 发射信号，通知主线程工作已完成
        self.finished.emit()

        print("结束线程")
