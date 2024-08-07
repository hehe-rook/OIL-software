def save_data(data=None, file_path=None, vt=None):
    from PyQt5.QtWidgets import QApplication, QFileDialog
    # 获取用户选择的文件夹路径
    folder_path = QFileDialog.getExistingDirectory(
        None, "Select Directory", "", QFileDialog.ShowDirsOnly
    )
    # 检查是否选择了文件夹
    if folder_path:
        # 在此处将您的数据保存到所选文件夹位置
        print("Selected folder:", folder_path)
    else:
        print("No folder selected.")

    # try:
    #     with open(file_path, 'w') as file:
    #         for item in data:
    #             file.write(str(item) + '\n')
    #     print("Data saved successfully.")
    # except Exception as e:
    #     print("Error occurred while saving data:", e)


def judge_file(data, item, parent_item, parent_parent_item):
    if not parent_item:  # 没得父节点
        # 选择的是topItem
        data = data[item]
        # "岩相预测数据"
        if item == "训练模型":
            vt = [{'vt': 'pt'} if key == "LSTMClassifier" else {'vt': 'joblib'}
                  for key, value in data.items() for subkey, subvalue in value.items()]
        else:
            vt = 'xlsx'
        item_data = [{f"{item}_{key}_{subkey}":
                          subvalue} for key, value in data.items() for subkey, subvalue in value.items()]

    else:  # 有父节点

        if not parent_parent_item:  # 没得爷节点
            # 选择的是topItem
            if parent_item == "训练模型":
                vt = [{'vt': 'pt'} if item == "LSTMClassifier" else {'vt': 'joblib'}
                      for key, value in data.items()]
            else:
                vt = 'xlsx'
            data = data[parent_item][item]
            item_data = {f"{parent_item}_{item}_{key}": value for key, value in data.items()}
        else:  # 有爷节点
            if parent_parent_item == "训练模型":
                vt = [{'vt': 'pt'} if parent_item == "LSTMClassifier" else {'vt': 'joblib'}]
            else:
                vt = 'xlsx'
            item_data = {f"{parent_parent_item}_{parent_item}_{item}": data[parent_parent_item][parent_item][item]}
    save_data(item_data, vt)
    print(item_data, vt)
