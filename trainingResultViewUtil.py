import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.patches as mpatches

from fracture_parameter.arps.dca import ArpsCurve
from util.pltUtil import remove_widget

plt.rcParams["font.sans-serif"] = "SimHei"
plt.rcParams["axes.unicode_minus"] = False
facies_labels = ['黑色煤', '灰黑色泥岩',
                 '灰黑色碳质泥岩',
                 '灰色粉砂质泥岩',
                 '灰色含气细砂岩',
                 '灰色泥岩',
                 '灰色泥质砂岩',
                 '灰色细砂岩',
                 '浅灰色含气细砂岩',
                 '浅灰色含气中砂岩',
                 '浅灰色细砂岩',
                 '深灰色泥岩']
facies_dict = {
    '黑色煤': 1,
    '灰黑色泥岩': 2,
    '灰黑色碳质泥岩': 3,
    '灰色粉砂质泥岩': 4,
    '灰色含气细砂岩': 5,
    '灰色泥岩': 6,
    '灰色泥质砂岩': 7,
    '灰色细砂岩': 8,
    '浅灰色含气细砂岩': 9,
    '浅灰色含气中砂岩': 10,
    '浅灰色细砂岩': 11,
    '深灰色泥岩': 12
}
import matplotlib.colors as colors

cmap_facies = colors.ListedColormap(
    ['black', 'darkgray', 'brown', 'blue', 'cyan', 'green', 'yellow', 'orange', 'red', 'purple', 'pink',
     'lightgreen'],
    'indexed',
    len(facies_dict))


def Lithofacies_statistical_map(layout, param):
    """
    绘制3D井位图
    :param layout:
    :return:
    """
    remove_widget(layout)
    fig = Lithofacies_statistical_fig(param)
    canvas = FigureCanvas(fig)
    layout.addWidget(canvas)


def Lithofacies_statistical_fig(y_pred):
    """
    岩相统计图
    :return:
    """
    # count the number of unique entries for each facies, sort them by
    # facies number (instead of by number of entries)
    y_pred = pd.Series(y_pred)
    facies_counts = y_pred.value_counts().sort_index()
    print(facies_counts)
    fig = plt.figure(figsize=(6, 8))
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Microsoft YaHei', 'SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    # use facies labels to index each count
    print(facies_counts.index)
    # facies_counts.index = facies_labels
    facies_counts.index = [facies_labels[idx - 1] for idx in facies_counts.index]

    # 将colormap转换为颜色列表
    color_list = [cmap_facies.colors[i] for i in range(cmap_facies.N)]
    ax = facies_counts.plot(kind='bar', color=color_list, title='Distribution of Forecast Data by Facies')
    # 在每个条形上添加文本
    for p in ax.patches:
        ax.text(p.get_x() + p.get_width() / 2., p.get_height(), '%d' % int(p.get_height()),
                fontsize=12, color='black', ha='center', va='bottom')

    return fig


def Lithofacies_prediction_map(layout, data, y_pred, facies, logs, prediction):
    remove_widget(layout)
    if prediction:
        fig = Lithofacies_prediction_fig(data, y_pred, facies, logs)
    else:
        fig = Lithofacies_prediction_true_fig(data, y_pred, facies, logs)
    canvas = FigureCanvas(fig)
    layout.addWidget(canvas)


def Lithofacies_prediction_true_fig(data, y_pred, facies, logs):
    cols1 = len(logs) + 2  # +2 分别为真实岩相和预测岩相
    fig, ax = plt.subplots(nrows=1, ncols=cols1, figsize=(12, 6), sharey=True)
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Microsoft YaHei', 'SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.suptitle('WELL F02-1', size=15)
    print(data.columns)
    for i in range(cols1):
        if i < cols1 - 2:
            ax[i].plot(data[logs[i]], data['DEPT'], color='b', lw=0.5)
            ax[i].set_title('%s' % logs[i])
            ax[i].minorticks_on()
            ax[i].grid(which='major', linestyle='-', linewidth='0.5', color='lime')
            ax[i].grid(which='minor', linestyle=':', linewidth='0.5', color='black')
            ax[i].set_ylim(max(data['DEPT']), min(data['DEPT']))
        elif i == cols1 - 2:
            F = np.vstack((facies, facies)).T
            ax[i].imshow(F, aspect='auto', extent=[0, 1, max(data['DEPT']), min(data['DEPT'])], cmap=cmap_facies)
            ax[i].set_title('TRUE FACIES')
        elif i == cols1 - 1:
            F = np.vstack((y_pred, y_pred)).T
            ax[i].imshow(F, aspect='auto', extent=[0, 1, max(data['DEPT']), min(data['DEPT'])], cmap=cmap_facies)
            ax[i].set_title('PRED. FACIES')
    patches = [mpatches.Patch(color=cmap_facies.colors[i], label=facies_labels[i]) for i in range(len(facies_labels))]
    plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    return fig


def Lithofacies_prediction_fig(data, y_pred, facies, logs):
    """
    无真实值，只绘制测井曲线 及预测岩相视图
    :param data:
    :param y_pred:
    :param facies:
    :param logs:
    :return:
    """
    cols = len(logs) + 1
    fig, ax = plt.subplots(nrows=1, ncols=cols, figsize=(12, 6), sharey=True)
    plt.suptitle('WELL 007', size=15)
    for i in range(cols):
        if i < cols - 1:
            ax[i].plot(data[logs[i]], data['DEPT'], color='b', lw=0.5)
            ax[i].set_title('%s' % logs[i])
            ax[i].minorticks_on()
            ax[i].grid(which='major', linestyle='-', linewidth='0.5', color='lime')
            ax[i].grid(which='minor', linestyle=':', linewidth='0.5', color='black')
            ax[i].set_ylim(max(data['DEPT']), min(data['DEPT']))
        elif i == cols - 1:
            F = np.vstack((facies, facies)).T
            ax[i].imshow(F, aspect='auto', extent=[0, 12, max(data['DEPT']), min(data['DEPT'])], cmap=cmap_facies)
            ax[i].set_title('FACIES')
    # 创建一个图例来显示每种颜色对应的标签

    patches = [mpatches.Patch(color=cmap_facies.colors[i], label=facies_labels[i]) for i in range(len(facies_labels))]
    plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    return fig


def Log_correlation_analysis_map(layout, data, y_pred):
    remove_widget(layout)
    fig = Log_correlation_analysis_fig(data, y_pred)
    canvas = FigureCanvas(fig)
    layout.addWidget(canvas)


def Log_correlation_analysis_fig(data, y_pred):
    import matplotlib as mpl
    import seaborn as sns
    fig = plt.figure()
    # 设置Matplotlib字体，用于解决警告问题
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Microsoft YaHei', 'SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    # 设置中文字体
    # from matplotlib.font_manager import FontProperties
    # font = FontProperties(fname="SimHei.ttf")
    # sns.set(font=font.get_name())

    # 创建Seaborn绘图
    sns.set(style="whitegrid")
    tips = sns.load_dataset("tips")
    # Save plot display settings to change back to when done plotting with seaborn
    inline_rc = dict(mpl.rcParams)
    # Set seaborn style
    sns.set()
    # Define a color list
    color_list = ['black', 'darkgray', 'brown', 'blue', 'cyan', 'green', 'yellow', 'orange', 'red', 'purple', 'pink',
                  'lightgreen']
    # Add y_pred to the dataframe
    print(data.count())

    print(len(y_pred))
    data['y_pred'] = y_pred

    # Create a color map that maps y_pred values to colors
    color_map = {i + 1: color for i, color in enumerate(color_list)}
    # Drop the specified columns from the dataframe
    # 列出要检查和删除的列名
    columns_to_drop = ['FACIES', "A"]

    # 检查要删除的列是否存在并删除
    columns_to_drop_existing = [col for col in columns_to_drop if col in data.columns]
    print(columns_to_drop_existing)
    if columns_to_drop_existing:
        data_dropped = data.drop(columns_to_drop_existing, axis=1)
    else:
        data_dropped = data
    # Create a pairplot with the specified style
    sns.pairplot(data_dropped, hue='y_pred', palette=color_map, plot_kws={"s": 15})

    # Show the plot
    # plt.show()
    # plt.show()

    return plt.gcf()


import numpy as np
import pandas as pd
import sys
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

from fracture_parameter.arps.utils_ import DeclineCurve
# from utils_ import DeclineCurve
# import utils.DeclineCurve
from lmfit import Model


def productionForecast_map(layout, param):
    remove_widget(layout)
    # fig = predict_arps(data)
    # fig = ArpsCurve.predict_arps(
    #     prd_time_series='daily_production',
    #     well_nm='well002',  # 预测井
    #     liquid='OIL(BBL)',  # 流体类型
    #     qi_min=200,  # 参数取值区间
    #     b_min=0.3,
    #     di_min=1e-5,
    #     qi_max=1000,
    #     b_max=3,
    #     di_max=20,
    #     sigma_fit=2,
    #     sigma_pred=2,  # 置信区间
    #     pred_interval=4500  # 预测天数
    # )
    fig = ArpsCurve.predict_arps(
        prd_time_series='daily_production',
        param=param
    )
    canvas = FigureCanvas(fig)
    layout.addWidget(canvas)


# Use fitted equation from arps.fit_arps to create EUR prediction with CI intervals
def predict_arps(param, prd_time_series='daily_production'):
    well_nm = param["well_nm"]
    liquid = param["liquid"]
    qi_min = param["qi_min"]
    b_min = param["b_min"]
    di_min = param["di_min"]
    qi_max = param["qi_max"]
    b_max = param["b_max"]
    di_max = param["di_max"]
    sigma_fit = param["sigma_fit"]
    sigma_pred = param["sigma_pred"]
    pred_interval = param["pred_interval"]
    """
    prd_time_series: (str) a production time series in form of a csv
    well_nm: (str, int) the API, or well ID/ name
    liquid: (str) the type of liquid to calculuate EUR
    qi_min: (int) qi lower bound
    b_min: (int) bi lower bound
    di_min: (int) di lower bound
    qi_max: (int) qi upper bound
    b_max: (int) bi upper bound
    di_max: (int) di upper bound
    sigma_fit: (int) significance level for fitted curve
    sigma_pred: (int) significance level for predicted curve
    pred_interval: (float) future number of days to predict

    """

    # df = pd.read_csv(f"{prd_time_series}.csv")
    df = pd.read_csv("D:/File/24石工大赛/project/py/pyProject/fracture_parameter/daily_production.csv")

    df = df.astype({"API": str, f"{liquid}": float})
    df = df[(df[f"{liquid}"].notnull()) & (df[f"{liquid}"] > 0)]
    df["days"] = df.groupby("API").cumcount() + 1

    filtered_df = df[df.API == f"{well_nm}"]
    cumsum_days = filtered_df["days"]
    prod = filtered_df[f"{liquid}"]

    # plot data
    fig = plt.figure(figsize=(14, 6))  #
    plt.plot(cumsum_days, prod, label=f"{liquid}", linewidth=1)

    # build Model
    hmodel = Model(DeclineCurve.hyperbolic_equation)

    # create lmfit Parameters, named from the arguments of `hyperbolic_equation`
    # note that you really must provide initial values.

    # params = hmodel.make_params(qi=431.0371968722894, b=0.5443981508109322, di=0.006643764565975722)

    params = hmodel.make_params(qi=qi_max, b=b_max, di=di_max)

    # set bounds on parameters
    params["qi"].min = qi_min
    params["b"].min = b_min
    params["di"].min = di_min

    # do fit, print resulting parameters
    result = hmodel.fit(prod, params, t=cumsum_days)

    y = prod
    y_fit = result.best_fit

    ss_res = np.sum((y - y_fit) ** 2)
    # total sum of squares
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    # r-squared
    r2 = 1 - (ss_res / ss_tot)
    print(result.fit_report())
    print("R-Square: ", str(round(r2 * 100, 3)) + "%")

    # plot best fit: not that great of fit, really

    plt.plot(cumsum_days, result.best_fit, "r--", label="Arps拟合", linewidth=3)

    # calculate the (1 sigma) uncertainty in the predicted model
    # and plot that as a confidence band
    dprod = result.eval_uncertainty(result.params, sigma=sigma_fit)
    plt.fill_between(
        cumsum_days,
        result.best_fit - dprod,
        result.best_fit + dprod,
        color="#AB8888",
        label="uncertainty band of fit",
    )

    # now evaluate the model for other values, predicting future values
    future_days = np.array(np.arange(max(cumsum_days + 1), pred_interval))
    future_prod = result.eval(t=future_days)
    eur = sum(prod) + sum(future_prod)

    plt.plot(future_days, future_prod, "k--", label="prediction")

    # ...and calculate the 1-sigma uncertainty in the future prediction
    # for 95% confidence level, you'd want to use `sigma=2` here:
    future_dprod = result.eval_uncertainty(t=future_days, sigma=sigma_pred)

    # print("### Prediction/n# Day  Prod     Uncertainty")

    # for day, prod, eps in zip(future_days, future_prod, future_dprod):
    #     print(" {:.1f}   {:.1f} +/- {:.1f}".format(day, prod, eps))

    plt.fill_between(
        future_days,
        future_prod - future_dprod,
        future_prod + future_dprod,
        color="#ABABAB",
        label="uncertainty band of prediction",
    )

    plt.legend(loc="upper right")
    print("EUR: ", eur)
    # plt.show()
    return fig
