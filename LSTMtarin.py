import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
import pandas as pd


# 读取数据


# 定义损失函数和优化器
# 选择损失函数
def select_loss_function(loss_function):
    if loss_function == 'CrossEntropyLoss':
        return nn.CrossEntropyLoss()
    elif loss_function == 'MSELoss':
        return nn.MSELoss()
    elif loss_function == 'BCELoss':
        return nn.BCELoss()
    elif loss_function == 'NLLLoss':
        return nn.NLLLoss()
    elif loss_function == 'SmoothL1Loss':
        return nn.SmoothL1Loss()
    else:
        return nn.CrossEntropyLoss()


# 选择优化器
def select_optimizer(optimizer, model, learning_rate):
    if optimizer == 'Adam':
        return optim.Adam(model.parameters(), lr=learning_rate)
    elif optimizer == 'SGD':
        return optim.SGD(model.parameters(), lr=learning_rate)
    elif optimizer == 'RMSprop':
        return optim.RMSprop(model.parameters(), lr=learning_rate)
    elif optimizer == 'Adagrad':
        return optim.Adagrad(model.parameters(), lr=learning_rate)
    elif optimizer == 'Adamax':
        return optim.Adamax(model.parameters(), lr=learning_rate)
    else:
        return optim.Adam(model.parameters(), lr=learning_rate)


class LSTMClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, num_layers, dropout):
        super(LSTMClassifier, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers=num_layers, batch_first=True, dropout=dropout)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        lstm_out = lstm_out[:, -1]
        output = self.fc(lstm_out)
        return output


# 定义LSTM模型
def train_model(train_data, train_labels, params, input_dim):
    # 创建模型实例
    model = LSTMClassifier(input_dim, params['hidden_dim'], 12, params['num_layers'],
                           params['dropout'])
    # 选择损失函数
    criterion = select_loss_function(params['loss_function'])
    # 选择优化器
    optimizer = select_optimizer(params['optimizer'], model, params['learning_rate'])
    # 训练模型
    for epoch in range(params['epochs']):
        model.zero_grad()
        output = model(train_data)
        loss = criterion(output, train_labels.view(-1))
        loss.backward()
        optimizer.step()

    print("Training complete.")
    return model


def LSTM_classifier(data, params, sel_train_list):
    train_data = data[sel_train_list].values
    input_dim = train_data.shape[1]  # 获取特征数量
    train_data2, test_data, train_labels2, test_labels = train_test_split(
        data[sel_train_list].values,
        data['FACIES'].values,
        test_size=0.2,
        random_state=42
    )
    train_labels = data['FACIES'].values
    # 将所有目标值减1
    train_labels = train_labels - 1
    test_labels = test_labels - 1
    # 转换为PyTorch张量
    train_data = torch.tensor(train_data, dtype=torch.float)
    train_data = train_data.unsqueeze(1)

    train_labels = torch.tensor(train_labels, dtype=torch.long).view(-1, 1)
    # 测试数据也需要转换为PyTorch张量
    test_data = torch.tensor(test_data, dtype=torch.float)
    test_data = test_data.unsqueeze(1)
    test_data = train_data
    test_labels = torch.tensor(test_labels, dtype=torch.long).view(-1, 1)
    test_labels = train_labels
    # 假设输入维度为7（你的特征数量），隐藏层维度为50，输出维度为12（你的类别数量）
    modelfinal = train_model(train_data, train_labels, params, input_dim)
    # 测试模型
    modelfinal.eval()
    with torch.no_grad():
        output = modelfinal(test_data)
        criterion = select_loss_function(params['loss_function'])
        loss = criterion(output, test_labels.view(-1))
        print(f"Test Loss: {loss.item()}")

        # 计算准确率
        _, predicted = torch.max(output, 1)
        predicted = predicted + 1
        predicted = predicted.numpy()
        return predicted, modelfinal
        # # Create the inverse mapping dictionary
        # inverse_facies_dict = {v: k for k, v in facies_dict.items()}
        #
        # # Convert the predicted values back to their original form
        # predicted_original = [inverse_facies_dict[i] for i in predicted.numpy()]
        # print(predicted_original)

        # correct = (predicted == test_labels.view(-1)).sum().item()
        # accuracy = correct / test_labels.size(0)
        # print(f"Test Accuracy: {accuracy * 100}%")

        # torch.save(modelfinal, 'lstmmodeltruemodelfinal1.pt')

#
# if __name__ == '__main__':
#     # 将'FACIES'列转换为数值
#     data = pd.read_excel('test007.xlsx')
#     facies_dict = {
#         '黑色煤': 1,
#         '灰黑色泥岩': 2,
#         '灰黑色碳质泥岩': 3,
#         '灰色粉砂质泥岩': 4,
#         '灰色含气细砂岩': 5,
#         '灰色泥岩': 6,
#         '灰色泥质砂岩': 7,
#         '灰色细砂岩': 8,
#         '浅灰色含气细砂岩': 9,
#         '浅灰色含气中砂岩': 10,
#         '浅灰色细砂岩': 11,
#         '深灰色泥岩': 12
#     }
#     data['FACIES'] = data['FACIES'].map(facies_dict)
#     # 划分训练集和测试集
#     # sel_train_list = ['GR', 'SP.MV', 'CAL.', 'AC.', 'CNL.V/V', 'LLD', 'LLS.OHMM']
#     sel_train_list = ['GR', 'SP', 'CAL', 'AC', 'CNL', 'LLD', 'LLS']
#     train_data = data[sel_train_list].values
#     params = {
#         'hidden_dim': 128,
#         'num_layers': 2,
#         'dropout': 0.3,
#         'loss_function': 'CrossEntropyLoss',
#         'optimizer': 'Adam',
#         'learning_rate': 0.001,
#         'epochs': 1000
#     }
#     LSTM_classifier(data, params, sel_train_list)
