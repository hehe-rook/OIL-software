import pandas as pd
import numpy as np
import numpy as np
import matplotlib.pyplot as plt

# 假设数据存储在名为 'well_log_data.csv' 的CSV文件中，包含了上述列名
# 将数据加载到pandas DataFrame中
df = pd.read_excel('007facies.xlsx')
print(df)


# # 定义计算所需的常数（这些值可能因地区和岩性而异，需要根据实际情况调整）

#

# 计算孔隙度
def calculate_porosity(density_log, matrix_density, fluid_density):
    porosity = (matrix_density - density_log) / (matrix_density - fluid_density)
    return np.clip(porosity, 0, 1)


# 计算泥质体积
def calculate_vsh(gamma_ray_log, gr_min, gr_max):
    # 泥质体积计算所需的常数（这是示例值）

    vsh = (gamma_ray_log - gr_min) / (gr_max - gr_min)
    vsh = np.clip(vsh, 0.1, 0.95)  # 确保VSH在0和1之间
    return vsh


# 计算含水饱和度
def calculate_sw(archie_porosity, deep_resistivity_log, rw, a, m, n):
    # Archie方程计算含水饱和度
    sw = (a / (archie_porosity ** m) * rw / deep_resistivity_log) ** (1 / n)
    sw = np.clip(sw, 0, 1)  # 确保Sw在0和1之间
    return sw


# 使用物质平衡方程计算气体饱和度(Sg)(示例值)
def calculate_sg(sw):
    sg = 1 - sw
    sg = np.clip(sg, 0, 1)
    return sg


# 计算渗透率
def calculate_perm(porosity):
    if porosity == 0:
        return 0
    else:
        k = (porosity ** 3 * (1 - porosity) ** 2) / (0.81 * (1 - porosity) ** 2)
        k = k * 100
        k = np.clip(k, 0, 2)
        return k


# 计算参数
def calculate_(df):
    a = 1.0  # Tortuosity factor
    m = 2.0  # Cementation exponent
    n = 2.0  # Saturation exponent
    rw = 0.05  # Formation water resistivity
    matrix_density = 2.65  # 岩石基质的密度
    fluid_density = 1.0  # 流体的密度
    gr_min = 50  # 清洁地层的最小伽马射线值
    gr_max = 160  # 泥质地层的最大伽马射线值
    df['POR'] = calculate_porosity(df['DEN.'], matrix_density, fluid_density)
    df['VSH'] = calculate_vsh(df['GR'], gr_min, gr_max)
    df['Sw'] = calculate_sw(df['POR'], df['LLD'], rw, a, m, n)
    df['PERM'] = df['POR'].apply(calculate_perm)

    # 假设Sg无法直接从给定的测井数据中计算，需要额外的数据
    df['Sg'] = calculate_sg(df['Sw'])  # 用于气饱和度的占位符
    depth = df['DEPT.M']
    return df, depth


df, depth = calculate_(df)


def relative_permeability(Sg, n, m):
    k_rg = Sg ** n
    k_rw = (1 - Sg) ** m
    return k_rg, k_rw


# 定义经验参数
n = 1.5
m = 2.2

import matplotlib.pyplot as plt


def plot_relative_permeability(depth_start, depth_end):
    # 选择特定深度区间的数据
    max_depth = df['DEPT.M'].max()
    if depth_end > max_depth:
        depth_end = depth_start - 20
    dataindex = df[(df['DEPT.M'] >= depth_start) & (df['DEPT.M'] <= depth_end)]

    # 如果没有找到对应深度的数据，打印错误信息并返回
    if dataindex.empty:
        print(f"No data found at depth range {depth_start} ")
        print(f"All data depth range: {df['DEPT.M'].min()} to {df['DEPT.M'].max()}")
        return
    # 计算相对渗透率
    Sg = dataindex['Sg'].values
    Sg.sort()

    k_rg, k_rw = relative_permeability(Sg, n, m)

    # 绘制曲线
    plt.figure(figsize=(10, 6))
    plt.plot(1 - Sg, k_rg, label='Gas')
    plt.plot(1 - Sg, k_rw, label='Water')
    plt.xlabel('Gas Saturation')
    plt.ylabel('Relative Permeability')
    plt.title(f'Relative Permeability from Depth {depth_start}')
    plt.legend()
    plt.show()


# 使用函数生成图像
a = 2641.11
plot_relative_permeability(a, a + 20)  # 生成深度为1000到2000的相对渗透率曲线

import matplotlib.pyplot as plt


# 定义参数列表
def plt1(df):
    params = ['POR', 'VSH', 'Sw', 'PERM', 'Sg']

    # 创建一个新的figure
    fig, axs = plt.subplots(1, len(params), figsize=(15, 6))
    plt.rcParams["font.sans-serif"] = "SimHei"
    plt.rcParams["axes.unicode_minus"] = False

    # 为每个参数创建一个子图
    for i, param in enumerate(params):
        ax = axs[i]
        ax.boxplot(df[param])
        ax.set_title(f'{param} Boxplot')
        ax.set_ylabel(param)

    plt.tight_layout()
    plt.show()


plt1(df)
# 添加解释
print("解释：")
print("1. 箱子：表示数据的四分位距，即数据的中间50%的范围。")
print("2. 中线：表示数据的中位数。")
print("3. 须：表示数据的范围（最小值和最大值）。")
print("4. 异常值：如果有的话，用点表示，表示离群的数据点，即那些远离箱子的值。")


def plot_distributions(df, depth):
    # 创建一个新的figure
    # 创建一个新的figure
    fig, axs = plt.subplots(5, 1, figsize=(8, 12))

    # 绘制孔隙度(POR)的线图
    axs[0].plot(depth, df['POR'], color='blue')
    axs[0].set_title('Porosity vs Depth')
    axs[0].set_ylabel('Porosity')

    # 绘制泥质体积(VSH)的线图
    axs[1].plot(depth, df['VSH'], color='green')
    axs[1].set_title('Vshale vs Depth')
    axs[1].set_ylabel('Vshale')

    # 绘制含水饱和度(Sw)的线图
    axs[2].plot(depth, df['Sw'], color='red')
    axs[2].set_title('Water Saturation vs Depth')
    axs[2].set_ylabel('Water Saturation')

    # 绘制渗透率(PERM)的线图
    axs[3].plot(depth, df['PERM'], color='purple')
    axs[3].set_title('Permeability vs Depth')
    axs[3].set_ylabel('Permeability')

    # 绘制气体饱和度(Sg)的线图
    axs[4].plot(depth, df['Sg'], color='orange')
    axs[4].set_title('Gas Saturation vs Depth')
    axs[4].set_ylabel('Gas Saturation')

    # 显示图形
    plt.tight_layout()
    plt.show()


def plot_distributions_2(df, depth):
    # 创建一个新的figure
    # 创建一个新的figure
    fig, axs = plt.subplots(1, 5, figsize=(8, 12))

    # 绘制孔隙度(POR)的线图
    axs[0].plot(df['POR'], depth, color='blue')
    axs[0].set_title('Porosity vs Depth')
    axs[0].set_ylabel('Porosity')

    # 绘制泥质体积(VSH)的线图
    axs[1].plot(df['VSH'], depth, color='green')
    axs[1].set_title('Vshale vs Depth')
    axs[1].set_ylabel('Vshale')

    # 绘制含水饱和度(Sw)的线图
    axs[2].plot(df['Sw'], depth, color='red')
    axs[2].set_title('Water Saturation vs Depth')
    axs[2].set_ylabel('Water Saturation')

    # 绘制渗透率(PERM)的线图
    axs[3].plot(df['PERM'], depth, color='purple')
    axs[3].set_title('Permeability vs Depth')
    axs[3].set_ylabel('Permeability')

    # 绘制气体饱和度(Sg)的线图
    axs[4].plot(df['Sg'], depth, color='orange')
    axs[4].set_title('Gas Saturation vs Depth')
    axs[4].set_ylabel('Gas Saturation')

    # 显示图形
    plt.tight_layout()
    plt.show()


plot_distributions_2(df, depth)

# import matplotlib.pyplot as plt
#
#
# # 假设 'df' 是包含测井数据和计算参数的DataFrame
#
# # 定义函数以绘制测井曲线
# def plot_well_log_curves(df, depth_col, curve_cols):
#     # 创建一个图形和一组子图
#     fig, axs = plt.subplots(1, len(curve_cols), figsize=(15, 10), sharey=True)
#     # 定义一个颜色列表
#     colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
#
#     for i, col in enumerate(curve_cols):
#         axs[i].plot(df[col], df[depth_col], color=colors[i % len(colors)])
#         axs[i].set_xlabel(col)
#         axs[i].invert_yaxis()  # 反转y轴，使深度向下增加
#         axs[i].grid(True)
#
#     # 设置y轴标签
#     axs[0].set_ylabel(depth_col)
#
#     # 调整布局
#     plt.tight_layout()
#
#     # 显示图形
#     plt.show()


# # 定义深度列和要绘制的曲线列
# depth_col = 'DEPT.M'
# curve_cols = ['GR', 'SP.MV', 'CAL.', 'AC.', 'CNL.V/V', 'LLD', 'LLS.OHMM', 'POR', 'VSH', 'Sw', 'PERM', 'Sg']
#
# # 调用函数以绘制测井曲线
# plot_well_log_curves(df, depth_col, curve_cols)

# 将计算得到的参数保存到新的CSV文件中
# df.to_csv('calculated_parameters007.csv', index=False)
#
# print("计算得到的参数已保存到 'calculated_parameters.csv' 文件中。")
