from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from util.pltUtil import remove_widget
from util.wellhead import figWellhead
from adjustText import adjust_text
import matplotlib.pyplot as plt


def draw_well_2D(layout, filePath):
    """
    绘制3D井位图
    :param layout:
    :return:
    """
    print(draw_well_2D.__name__)
    # 创建布局
    # 调用绘图函数并将图像嵌入到 PyQt 窗体中
    # print(layout.count())

    remove_widget(layout)
    # df = pd.read_excel(filePath)
    df = filePath
    fig = figWellhead(df)
    canvas = FigureCanvas(fig)
    layout.addWidget(canvas)


def figWellhead(df):
    # 假设你已经读取了数据
    # df = pd.read_excel("data.xlsx")

    # 创建图形
    fig = plt.figure(figsize=(6, 8))
    # plt.scatter(df['井口坐标x'], df['井口坐标y'])
    print(df)
    plt.scatter(df['x'], df['y'])
    # 创建一个空的文本列表
    texts = []

    # 在每个井位上添加井号到文本列表
    for i, txt in enumerate(df['well']):
        texts.append(plt.text(df['x'][i], df['y'][i], txt))

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
