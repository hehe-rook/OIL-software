import pandas as pd


# 定义一个函数来读取.LAS文件并将其转换为DataFrame
def read_las_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    curve_type = []
    # 找到包含"LG--CV-CL--M"的行的索引
    curve_type_start_index = next(i for i, line in enumerate(lines) if "LG--CV-CL--M" in line)  # 曲线类型记录 开始行
    curve_type_end_index = next(
        i for i, line in enumerate(lines) if "~Parameter Information Section" in line)  # 曲线类型记录 结束行
    curve_type = [line.split()[0].split('.')[0] for line in lines[curve_type_start_index + 1:curve_type_end_index]]
    # 找到包含"~A"的行的索引
    start_index = next(i for i, line in enumerate(lines) if "~A" in line)
    # 读取数据行并将它们转换为列表
    data = [list(map(float, line.split())) for line in lines[start_index + 1:]]
    # 将数据转换为DataFrame
    df = pd.DataFrame(data, columns=curve_type)
    return curve_type, df

# # 调用函数来读取.LAS文件
# df = read_las_file("T010.LAS")
#
# # 将DataFrame保存为Excel文件
# df.to_excel("data.xlsx", index=False)
#
# # 打印成功消息
# print("The data from data.las was successfully saved to data.xlsx")
