import torch
import torch.nn as nn
# 加载模型
import pandas as pd
from joblib import load
from matplotlib import pyplot as plt
from faciestest.plots import plotlogsprec, plotlogs
from faciestest.plots import testplotlogs


# 定义LSTM模型
class LSTMClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(LSTMClassifier, self).__init__()
        self.hidden_dim = hidden_dim
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        lstm_out = lstm_out[:, -1]
        output = self.fc(lstm_out)
        return output


def LSTM_lithofacies_pred(data, model):
    model.eval()
    # test_data = data[['GR', 'SP.MV', 'CAL.', 'AC.', 'CNL.V/V', 'LLD', 'LLS.OHMM']].copy()
    # 假设要确保 DataFrame 中包含 clo 列，如果不存在则填充为 0
    data_cloum = ['GR', 'SP', 'CAL', 'AC', 'CNL', 'LLD', 'LLS']
    for clo in data_cloum:
        if clo not in data:
            data[clo] = data.get(clo, 0)
    test_data = data[['GR', 'SP', 'CAL', 'AC', 'CNL', 'LLD', 'LLS']].copy()

    # test_data['LLS.OHMM'] = 0  # 将 'LLS.OHMM' 的值设置为0
    test_data = test_data.values
    logs = data.columns[1:]

    test_data = torch.tensor(test_data, dtype=torch.float)
    test_data = test_data.unsqueeze(1)

    # 使用模型进行预测
    with torch.no_grad():
        output = model(test_data)
        _, predicted = torch.max(output, 1)
        predicted = predicted + 1
        predicted_array = predicted.numpy()
        data['FACIES'] = predicted_array
        # facies = data['FACIES']
        # plt.rcParams["font.sans-serif"] = "SimHei"
        # plt.rcParams["axes.unicode_minus"] = False
        return data, predicted_array, logs
        # plotlogs(data, cols, rows, logs, facies)


def joblib_lithofacies_pred(data, model):
    logs = data.columns[1:]
    rows, cols = 1, 8
    # X_train = data[['GR', 'SP.MV', 'CAL.', 'AC.', 'CNL.V/V', 'LLD', 'LLS.OHMM']]
    X_train = data[['GR', 'SP', 'CAL', 'AC', 'CNL', 'LLD', 'LLS']]

    # 使用加载的模型进行预测
    y_pred = model.predict(X_train)
    data['FACIES'] = y_pred
    # facies = data['FACIES']
    return data, y_pred, logs
    # plt.rcParams["font.sans-serif"] = "SimHei"
    # plt.rcParams["axes.unicode_minus"] = False
    #
    # plotlogs(data, cols, rows, logs, facies)
    #
