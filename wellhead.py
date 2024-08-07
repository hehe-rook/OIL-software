import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from util.pltUtil import remove_widget


def figWellhead(df):
    # 假设数据存储在 "data.xlsx" 文件中
    # 文件格式: 序号, 井号, 井口坐标x, 井口坐标y, 海拔, 测量井深

    # 读取数据
    # 创建3D图形，并设置图形大小为(20, 15)以避免井位重叠
    fig = plt.figure(figsize=(20, 15))
    ax = fig.add_subplot(111, projection='3d')

    # 生成随机颜色
    colors = plt.cm.jet(np.linspace(0, 1, len(df)))

    # 对于每个井位，绘制从井口到井底的线，并在最上端显示井号
    for index, row in df.iterrows():
        # 井口坐标
        well_head = (row['x'], row['y'], row['KB'])
        # 井底坐标（假设井是垂直的，因此x和y坐标与井口相同）
        well_bottom = (row['x'], row['y'], row['KB'] - row['MD'])
        # 绘制线
        ax.plot([well_head[0], well_bottom[0]], [well_head[1], well_bottom[1]], [well_head[2], well_bottom[2]], 'r-')
        # 显示井号，并使用不同颜色
        ax.text(well_head[0], well_head[1], well_head[2], f"{row['well']}", color=colors[index])
    plt.rcParams["font.sans-serif"] = "SimHei"
    plt.rcParams["axes.unicode_minus"] = False
    # 设置图形标题和坐标轴标签
    ax.set_title('井位坐标可视化')
    ax.set_xlabel('井口坐标x')
    ax.set_ylabel('井口坐标y')
    ax.set_zlabel('海拔')

    # 设置坐标轴范围
    ax.set_xlim([0, 7000])
    ax.set_ylim([0, 10000])

    # 设置坐标轴的刻度间隔
    ax.xaxis.set_major_locator(plt.MaxNLocator(14))
    ax.yaxis.set_major_locator(plt.MaxNLocator(20))
    # plt.show()
    return fig


def drawWellhead(layout, filePath):
    """
    绘制3D井位图
    :param layout:
    :return:
    """
    print(drawWellhead.__name__)
    # 创建布局
    # 调用绘图函数并将图像嵌入到 PyQt 窗体中
    print(layout.count())
    remove_widget(layout)
    # df = pd.read_excel(filePath)
    fig = figWellhead(filePath)
    canvas = FigureCanvas(fig)
    layout.addWidget(canvas)
