import pandas as pd


# 定义一个函数来读取.LAS文件并将其转换为DataFrame
def read_las_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # 找到包含"~A"的行的索引
    start_index = next(i for i, line in enumerate(lines) if "~A" in line)

    # 读取数据行并将它们转换为列表
    data = [line.split() for line in lines[start_index + 1:]]

    # 将数据转换为DataFrame
    # df = pd.DataFrame(data, columns=["DEPT.M", "GR", "SP.MV", "CAL.", "AC.", "CNL.V/V", "DEN.", "LLD", "LLS.OHMM"])
    df = pd.DataFrame(data, columns=["DEPT", "GR", "SP", "CAL", "AC", "CNL", "DEN", "LLD", "LLS"])

    return df

# # 调用函数来读取.LAS文件
# df = read_las_file("T010.LAS")
#
# # 将DataFrame保存为Excel文件
# df.to_excel("data.xlsx", index=False)
#
# # 打印成功消息
# print("The data from data.las was successfully saved to data.xlsx")
