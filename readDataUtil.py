import re

import matplotlib.pyplot as plt
import pandas as pd
from PyQt5.QtWidgets import QFormLayout, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QSpinBox, QDoubleSpinBox, \
    QComboBox


def test_read_data(filepath):
    data = pd.read_excel(filepath)
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
    # Convert the 'FACIES' column to numeric
    data['FACIES'] = data['FACIES'].map(facies_dict)
    plt.rcParams["font.sans-serif"] = "SimHei"
    plt.rcParams["axes.unicode_minus"] = False
    return data


def read_dialog_DP_param(dialog_):
    DP_param_ = {
        "custom_training_model": True,  # 模型操作类型 默认自定义操作
        "data_filePath": None,
        # "": None,
        "sel_well": None,
        "model": None,
        "model_param": None,
        "DefaultModelName": None
    }
    traningModeL = {
        "Boosting类算法": "Boosting",
        "随机森林": "RandomForest",
    }

    if dialog_.import_training_model.isChecked():  # 导入模型
        DP_param_["custom_training_model"] = False
        # DP_param_["data_filePath"] = dialog_.lineEdit_sel_model.text()
        DP_param_["sel_well"] = dialog_.lineEdit_sel_wellname.text()
        DP_param_["model"] = dialog_.lineEdit_sel_model.text()
    elif dialog_.custom_training_model.isChecked():  # 自定义训练模型
        DP_param_["DefaultModelName"] = dialog_.lineEdit_modelname.text()
        DP_param_["data_filePath"] = dialog_.lineEdit_import_lithofacies_data.text()
        DP_param_["model"] = dialog_.comboBox_model.currentText()
        # 处理中文（转换）
        if DP_param_["model"] in traningModeL:
            DP_param_["model"] = traningModeL[DP_param_["model"]]
        current_index = dialog_.modeParamSet.currentIndex()
        current_widget = dialog_.modeParamSet.widget(current_index)
        # 递归遍历布局内所有子控件
        layout = current_widget.findChildren(QFormLayout)[0]

        def get_widgets(layout):
            widgets = []
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if isinstance(item, (QVBoxLayout, QHBoxLayout)):  # 如果是嵌套布局
                    widgets += get_widgets(item.layout())
                elif item.widget():  # 如果是控件
                    widgets.append(item.widget())
            return widgets

        widgets = get_widgets(layout)
        values = {}
        for widget in widgets:
            if isinstance(widget, QLabel):
                continue
            if isinstance(widget, QCheckBox):
                values[re.sub(DP_param_["model"] + '_', '', widget.objectName())] = widget.text()  # 将控件的值存入字典
            elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
                values[re.sub(DP_param_["model"] + '_', '', widget.objectName())] = widget.value()  # 将控件的值存入字典
            elif isinstance(widget, QComboBox):
                values[re.sub(DP_param_["model"] + '_', '', widget.objectName())] = widget.currentText()  # 将控件的值存入字典
        DP_param_["model_param"] = values
    return DP_param_


def read_dialog_sweetArea_param(dialog_):
    sweetArea_param_ = {
        "por_threshold": dialog_.por_threshold.value(),  # 模型操作类型 默认自定义操作
        "sw_threshold": dialog_.sw_threshold.value(),
        "sg_threshold": dialog_.sg_threshold.value(),
        "perm_threshold": dialog_.perm_threshold.value(),
        "pressure_threshold": dialog_.pressure_threshold.value(),
        "temperature_threshold": dialog_.temperature_threshold.value(),
        # "WOB_min": dialog_.WOB_min.value(),
        # "WOB_max": dialog_.WOB_max.value(),
        # "WURF_RPM_min": dialog_.WURF_RPM_min.value(),
        # "WURF_RPM_max": dialog_.WURF_RPM_max.value(),
    }
    return sweetArea_param_
