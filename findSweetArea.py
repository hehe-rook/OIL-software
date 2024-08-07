import seaborn as sns
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.patches as mpatches
from util.pltUtil import remove_widget


# def corr_heatmap(df, method='spearman', cmap='plasma', figsize=(12, 10)):
#     # Generate a mask for the upper triangle
#     mask = np.triu(np.ones_like(df.corr(method=method), dtype=bool))
#     # Set up the matplotlib figure
#     plt.figure(figsize=figsize)
#     # Draw the heatmap with the mask and correct aspect ratio
#     sns.heatmap(df.corr(method=method), mask=mask, cmap=cmap, annot=True, square=True, vmin=0, vmax=1)
#     plt.show()


def findSweetArea(param):
    df = pd.read_excel('qss/insert_db/007.xlsx')
    # All features without depth
    heatmap_data = df[df.columns[1:]]
    # Plot correlation heatmap
    # corr_heatmap(df[no_depth])
    # 假设适合压裂或射孔的岩相是'灰色含气细砂岩'和'浅灰色含气细砂岩'
    suitable_facies = [1, 5, 9, 10]
    # 定义适合射孔的条件
    # por_threshold = 0.03  # 请根据实际情况设定孔隙度阈值
    # sw_threshold = 0.8  # 请根据实际情况设定水饱和度阈值
    # sg_threshold = 0.1
    # perm_threshold = 0.4  # 请根据实际情况设定渗透率阈值
    pressure_threshold = param['pressure_threshold']  # 压力阈值，根据实际情况设定
    temperature_threshold = param['temperature_threshold']  # 温度阈值，根据实际情况设定
    # 寻找满足条件的深度
    df['suitable'] = (
            (df['POR'] > param['por_threshold']) &
            (df['Sw'] < param['sw_threshold']) &
            (df['Sg'] > param['sg_threshold']) &
            (df['PERM'] > param['perm_threshold']) &
            (df['FACIES'].isin(suitable_facies))
    )
    # 找出连续的深度范围
    # print(df)
    df['block'] = (df['suitable'].shift(1) != df['suitable']).astype(int).cumsum()
    # print(df['block'])
    suitable_blocks = df[df['suitable']].groupby('block')['DEPT.M'].agg(['min', 'max'])
    # print("最适合射孔的深度范围为：")
    # print(suitable_blocks)

    suitable_blocks_dict = suitable_blocks.to_dict()
    # print(suitable_blocks_dict)
    return heatmap_data, suitable_blocks_dict
    # import pickle
    #
    # with open('suitable_blocks.pkl', 'wb') as f:
    #     pickle.dump(suitable_blocks_dict, f)


def corr_heatmap(layout, data):
    remove_widget(layout)
    fig = corr_heatmap_fig(data)
    canvas = FigureCanvas(fig)
    layout.addWidget(canvas)


def corr_heatmap_fig(df, method='spearman', cmap='plasma', figsize=(12, 10)):
    # Generate a mask for the upper triangle
    mask = np.triu(np.ones_like(df.corr(method=method), dtype=bool))
    # Set up the matplotlib figure
    fig = plt.figure(figsize=figsize)
    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(df.corr(method=method), mask=mask, cmap=cmap, annot=True, square=True, vmin=0, vmax=1)

    return fig
