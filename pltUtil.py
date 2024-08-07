"""
matplotlib 绘图工具

"""
import sys
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from calculate import calcuswpor


# from calculate import calcuswpor


def well_log_curces(layout: object, df: object, depth_col: object, curve_cols: object) -> object:
    """
    测井曲线
    :param layout:
    :param df:
    :param depth_col:
    :param curve_cols:
    :return:
    """
    print(well_log_curces.__name__)
    remove_widget(layout)
    # 创建布局
    # layout = QVBoxLayout(self.chartView)
    # 调用绘图函数并将图像嵌入到 PyQt 窗体中
    fig = calcuswpor.plot_well_log_curves(df, depth_col, curve_cols)
    canvas = FigureCanvas(fig)
    layout.addWidget(canvas)


def drawLine_(layout):
    """
    曲线绘制测试
    :param self:
    :return:
    """
    print(drawLine_.__name__)
    # 创建布局
    # 调用绘图函数并将图像嵌入到 PyQt 窗体中
    remove_widget(layout)
    fig = drawLine()
    canvas = FigureCanvas(fig)
    layout.addWidget(canvas)


def drawLine():
    # 创建一个图形和一组子图
    fig, axs = plt.subplots(1, 1, figsize=(15, 10), sharey=True)
    x = [1, 2, 3, 4]
    y = [1, 2, 3, 4]
    axs.plot(x, y)
    axs.set_xlabel('X Axis')
    axs.set_ylabel('Y Axis')
    axs.set_title('Line Plot')
    # 调整布局
    plt.tight_layout()
    return fig  # 返回图形对象


def remove_widget(layout):
    # print(layout.count())
    if layout.count() > 0:
        # layout.removeWidget(layout.itemAt(0).widget())
        layout.itemAt(0).widget().deleteLater()
