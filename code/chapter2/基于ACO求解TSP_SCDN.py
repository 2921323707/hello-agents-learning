'''
题目:基于ACO蚁群算法求解TSP
姓名:嘟嘟可大魔王
时间:2025/12/30
'''

import numpy as np
import matplotlib.pyplot as plt
import time

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei'] # 使用微软雅黑字体
plt.rcParams['axes.unicode_minus'] = False  # 处理负号显示异常

# 初始城市位置的散点图
def GetDistanceMatrix(X,Y,CityCount):
    '''
    计算城市之间的距离矩阵
    X:城市的横坐标
    Y:城市的纵坐标
    CityCount:城市数量
    '''
    plt.figure(1) # 创建图形窗口
    plt.plot(X,Y,'o')
    plt.xlabel("横坐标",fontproperties = 'Simhei')
    plt.ylabel("纵坐标",fontproperties = 'Simhei')
    plt.title("城市位置散点图",fontproperties = 'Simhei')
    plt.show()

    # 生成一个方阵作为任意两城市之间的距离矩阵
    #count行count列
    DistanceMatrix = np.zeros((CityCount,CityCount))
    for row in range(CityCount):
        for col in range(CityCount):
            DistanceMatrix[row,col] = pow((X[0,row] - X[0,col]) ** 2 + (Y[0,row] - Y[0,col]) ** 2,0.5)
    return DistanceMatrix




