import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import interpolate
import seaborn as sns

plt.rcParams['font.size'] = 20
from pyswarm import pso

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingRegressor

# Ignore user warning
import warnings

warnings.simplefilter('ignore', UserWarning)


# Create a function for prediction
def predict(model, Depth, PHIF, VSH, SW, KLOGH, WOB, SURF_RPM):
    # Make a test input
    X_test = np.array([Depth, WOB, SURF_RPM, PHIF, VSH, SW, KLOGH])
    X_test = X_test.reshape(1, -1)

    # Predict on a test input
    y_pred = model.predict(X_test)
    return y_pred[0]


def DrillingOptimize(param, data=None):
    df = pd.read_csv('qss/insert_db/Data_for_ROP_optimization.csv')
    # Separate feature and target
    X = df.drop(['ROP_AVG'], axis=1)
    y = df['ROP_AVG']
    # Train test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,
                                                        random_state=10)

    # Make pipeline
    steps = [('scaler', StandardScaler()),
             ('gbr', GradientBoostingRegressor(min_samples_leaf=6, max_depth=20,
                                               random_state=10))]
    pipe = Pipeline(steps)

    # Fit pipeline to training data
    pipe.fit(X_train, y_train)

    # Evaluate model with R2 metric
    train_score = pipe.score(X_train, y_train)
    test_score = pipe.score(X_test, y_test)
    print(f'R2 on train set: {train_score:.2f}')
    print(f'R2 on test set: {test_score:.2f}')

    # Predict on new inputs
    y_pred = predict(pipe, 4000, 0.2, 0.5, 1, 500, WOB=5e4, SURF_RPM=2)
    print(y_pred)

    #
    #
    # Define objective function. "pipe" as model
    # def fun(X):
    #     return -pipe.predict(X.reshape(1, -1))  # Minus sign to optimize
    fun = lambda X: -pipe.predict(X.reshape(1, -1))
    import pickle
    # with open('D:/File/24石工大赛/project/py/pyProject/fracture_parameter/suitable_blocks.pkl', 'rb') as f:
    #     suitable_blocks_dict = pickle.load(f)
    # a = suitable_blocks_dict
    # a = data
    # import numpy as np
    # 将 'min' 和 'max' 对应的值转换为数组
    # min_values = list(a['min'].values())
    # max_values = list(a['max'].values())
    # for min, max in zip(min_values, max_values):
    #     print(min, max)
    #
    # 现在，min_values 和 max_values 都是数组
    # Lower bounds of feature variables in the order of X.columns
    # lb = np.array([3480, 2e4, 1.5, 0.09, 0.1, 1, 0.001])
    # # Upper bounds of feature variables in the order of X.columns
    # ub = np.array([3500, 9e4, 2.5, 0.09, 0.1, 1, 0.001])
    # lb[0] = min
    # ub[0] = max
    # lb[1] = param["WOB_min"]
    # ub[1] = param["WOB_max"]
    # lb[2] = param["WURF_RPM_min"]
    # ub[2] = param["WURF_RPM_max"]
    # ub += 1e-10
    # Lower bounds of feature variables in the order of X.columns
    lb = np.array([param["Depth_min"], param["WOB_min"], param["WURF_RPM_min"], 0.09, 0.1, 1, 0.001])
    # Upper bounds of feature variables in the order of X.columns
    ub = np.array([param["Depth_max"], param["WOB_max"], param["WURF_RPM_max"], 0.09, 0.1, 1, 0.001])
    ub += 1e-10
    # Solve optimization
    xopt, fopt = pso(fun, lb, ub, swarmsize=200, omega=0.3, phip=.5,
                     phig=0.7, maxiter=1000, minstep=1e-8)
    # Print values that causes maximum ROP from xopt
    for i in range(len(X.columns)):
        print(f'{X.columns[i]}: {xopt[i]:.2f}')

    # Print value of maximum ROP from popt
    print(f'Maximum ROP achieved: {-fopt}')
# DrillingOptimize(param)
