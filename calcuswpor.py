import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

a = 1.0  # Tortuosity factor
m = 2.0  # Cementation exponent
n = 2.0  # Saturation exponent
rw = 0.05  # Formation water resistivity
matrix_density = 2.65  # 岩石基质的密度
fluid_density = 1.0  # 流体的密度
gr_min = 50  # 清洁地层的最小伽马射线值
gr_max = 160  # 泥质地层的最大伽马射线值


# 计算孔隙度
def calculate_porosity(density_log):
    porosity = (matrix_density - density_log) / (matrix_density - fluid_density)
    return np.clip(porosity, 0, 1)


# 计算泥质体积
def calculate_vsh(gamma_ray_log):
    # 泥质体积计算所需的常数（这是示例值）

    vsh = (gamma_ray_log - gr_min) / (gr_max - gr_min)
    vsh = np.clip(vsh, 0.1, 0.95)  # 确保VSH在0和1之间
    return vsh


# 计算含水饱和度
def calculate_sw(archie_porosity, deep_resistivity_log):
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


# 定义函数以绘制测井曲线
def plot_well_log_curves(df, depth_col, curve_cols):
    print("画图")
    # 创建一个图形和一组子图
    fig, axs = plt.subplots(1, len(curve_cols), figsize=(15, 10), sharey=True)
    # 定义一个颜色列表
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    if len(curve_cols) == 1:
        for i, col in enumerate(curve_cols):
            axs.plot(df[col], df[depth_col], color=colors[i % len(colors)])
            axs.set_xlabel(col)
            axs.invert_yaxis()  # 反转y轴，使深度向下增加
            axs.grid(True)
        # 设置y轴标签
        axs.set_ylabel(depth_col)
    else:
        for i, col in enumerate(curve_cols):
            axs[i].plot(df[col], df[depth_col], color=colors[i % len(colors)])
            axs[i].set_xlabel(col)
            axs[i].invert_yaxis()  # 反转y轴，使深度向下增加
            axs[i].grid(True)
        # 设置y轴标签
        axs[0].set_ylabel(depth_col)
    # 调整布局
    plt.tight_layout()
    # plt.show()
    print("结束")

    return fig  # 返回图形对象


# 定义深度列和要绘制的曲线列
# depth_col = 'DEPT.M'
# curve_cols = ['GR', 'SP.MV', 'CAL.', 'AC.', 'CNL.V/V', 'LLD', 'LLS.OHMM', 'POR', 'VSH', 'Sw', 'PERM', 'Sg']
depth_col = 'DEPT'
curve_cols = ['GR', 'SP', 'CAL', 'AC', 'CNL', 'LLD', 'LLS', 'POR', 'VSH', 'Sw', 'PERM', 'Sg']


# # 将计算得到的参数保存到新的CSV文件中
# df.to_csv('calculated_parameters.csv', index=False)
# print("计算得到的参数已保存到 'calculated_parameters.csv' 文件中。")

def getData(filepath):
    # 假设数据存储在名为 'well_log_data.csv' 的CSV文件中，包含了上述列名
    # 将数据加载到pandas DataFrame中
    df = pd.read_excel(filepath)
    # # 定义计算所需的常数（这些值可能因地区和岩性而异，需要根据实际情况调整）
    df['POR'] = calculate_porosity(df['DEN.'])
    df['VSH'] = calculate_vsh(df['GR'])
    df['Sw'] = calculate_sw(df['POR'], df['LLD'])
    df['PERM'] = df['POR'].apply(calculate_perm)
    # 假设Sg无法直接从给定的测井数据中计算，需要额外的数据
    df['Sg'] = calculate_sg(df['Sw'])  # 用于气饱和度的占位符
    return df


if __name__ == '__main__':
    # 调用函数以绘制测井曲线
    filepath = "well_log_data.xlsx"
    plot_well_log_curves(getData(filepath), depth_col, curve_cols)
