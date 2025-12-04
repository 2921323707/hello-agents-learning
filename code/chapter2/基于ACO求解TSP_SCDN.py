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


#算法实现
def ACO_TCP(X:np.ndarray,Y:np.ndarray) -> tuple:
    '''  
    params:
        X:城市的横坐标
        Y:城市的纵坐标
    outputs:
        最优路径及其长度
    '''
    # 根据城市个数生成城市距离矩阵
    DistanceMatrix = GetDistanceMatrix(X,Y,CityCount)

    ##开始计时 ##
    start = time.time() 
    # 根据蚂蚁的数量为每一只蚂蚁随机分配初始城市
    AntPlaceVector = np.random.randint(0,CityCount,(1,AntCount))

    #========================================================
    # 接着随机生成一条路线来初始信息素矩阵
    # 3-> 5 > 4 > 1 > 2 > 0  (6)
    #permutation随机排列
    RandomRoute = np.random.permutation(np.arange(CityCount))

    # 计算该随机路径的长度
    TempLength = 0
    for i in range(CityCount-1):
        TempLength += DistanceMatrix[RandomRoute[i],RandomRoute[i+1]]
    TempLength += DistanceMatrix[RandomRoute[0],RandomRoute[CityCount-1]]

    PheromoneMatrix = np.full((CityCount,CityCount),1/ TempLength)
    
    for i in range(CityCount):
        PheromoneMatrix[i,i] = 0

    # ===========================================================

    for iteration in range(MaxIteration):
        print(f"第{iteration+1}轮迭代")

        # 创建一个禁忌表，用双重列表的形式进行定义
        TabooList = []
        for i in range(AntCount):
            TabooList.append([])
        
        for i in range(AntCount):
            TabooList[i].append(AntPlaceVector[0,i])
        
        for i in range(CityCount - 1):
            for ant in range(AntCount):
                ProbilityVector = np.zeros((1,CityCount))
                for city in range(CityCount):
                    if city in TabooList[ant]:
                        continue
                    #信息素？ 
                    TempPheromone  = PheromoneMatrix[TabooList[ant][len(TabooList[ant]) - 1],city]
                    # 启发函数？

                    #计算1/距离
                    TempHeuristicValue = 1 / DistanceMatrix[city,TabooList[ant][len(TabooList[ant]) - 1]]
                    # 计算概率
                    ProbilityVector[0,city] = TempPheromone ** Alpha * TempHeuristicValue ** Beta

                    Pro_Sum = np.sum(ProbilityVector,axis = 1)
                    ProbilityVector = ProbilityVector / Pro_Sum
                    # 轮盘法选择下一城市
                    Next_City = np.random.choice(np.arange(CityCount),p = ProbilityVector.ravel())
                    TabooList[ant].append(Next_City)

        # 计算每只蚂蚁的路径长度
        RouteLengths = []
        for ant in range(AntCount):
            TempLength = 0
            for i in range(CityCount-1):
                TempLength += DistanceMatrix[TabooList[ant][i],TabooList[ant][i+1]]
            TempLength += DistanceMatrix[TabooList[ant][0],TabooList[ant][CityCount-1]]
            RouteLengths.append(TempLength)


        BestRoute = TabooList[np.argmin(RouteLengths)]
        RouteRecordMin[0,iteration] = min(RouteLengths)
        RouteRecordMax[0,iteration] = max(RouteLengths)
        RouteRecordAve[0,iteration] = np.mean(RouteLengths)
        BestRoute=TabooList[RouteLengths.index(min(RouteLengths))]

        # 更新信息素矩阵
        New_PheromoneMatrix = np.zeros((CityCount,CityCount))
        for row in range(CityCount):
            for col in range(row+1):
                if row == col:
                    break 
                NewInfo = 0

                for ant in range(AntCount):
                    # 如果某只蚂蚁经过了该条路径，则会增加该路径上的信息素
                    Path = TabooList[ant]
                    for i in range(CityCount - 1):
                        if (Path[i] == row and Path[i+1] == col) or (Path[i] == col and Path[i+1] == row):
                            NewInfo += Q / RouteLengths[ant]
                    # 首尾相连的路径
                    if (Path[0] == row and Path[CityCount - 1] == col) or (Path[0] == col and Path[CityCount - 1] == row):
                        NewInfo += Q / RouteLengths[ant]
                New_PheromoneMatrix[row,col] = (1 - VolatilizationRate) * PheromoneMatrix[row,col] + VolatilizationRate * NewInfo
                New_PheromoneMatrix[col,row] = (1 - VolatilizationRate) * PheromoneMatrix[col,row] + VolatilizationRate * NewInfo
        PheromoneMatrix = New_PheromoneMatrix


     # 结束计时 ##
    end = time.time()
    Time_Gap = end-start
 
    # 迭代完成后最优环游路线的示意图
    X = X[0, :].tolist()
    Y = Y[0, :].tolist()
    x = []
    y = []
    for city in BestRoute:
        x.append(X[city])
        y.append(Y[city])
    x.append(X[BestRoute[0]])
    y.append(Y[BestRoute[0]])
 
    plt.figure(3)
    for j in range(len(BestRoute)):
        plt.quiver(x[j], y[j], x[j + 1] - x[j], y[j + 1] - y[j], color='r', width=0.005, angles='xy', scale=1,
                   scale_units='xy')
    plt.quiver(x[-1], y[-1], x[0] - x[-1], y[0] - y[-1], color='r', width=0.005, angles='xy', scale=1,
               scale_units='xy')
    plt.title("基于蚁群算法的TSP", fontproperties="Simhei")
    plt.show()
 
    ## 输出算法的运行时间和相关的最短、最长和平均路径长度
    print("算法的运行时间为",Time_Gap, "秒")
    print("最短环游路径的长度为：", RouteRecordMin[0, MaxIteration-1])
    print("最长环游路径的长度为：", RouteRecordMax[0, MaxIteration-1])
    print("平均环游路径的长度为：", RouteRecordAve[0, MaxIteration-1])


















if __name__ == '__main__':
        # 参数定义
    CityCount = 50  # 定义城市个数
    # uniform()生成10个二维数组，数值范围是0到2000
    City_X = np.random.uniform(0, 2000, (1, CityCount))
    City_Y = np.random.uniform(0, 2000, (1, CityCount))
 
    AntCount = 30  # 定义蚂蚁数量
    MaxIteration = 200  # 定义最大迭代次数
    Alpha = 3  # 定义信息素因子
    Beta = 4  # 定义启发函数因子
    Q = 100  # 定义算法信息素常数
    VolatilizationRate = 0.5  # 定义算法中的挥发率


    # 其他变量定义
    np.random.seed(2)  # 固定随机数种子，方便多次进行验证
    RouteRecordMin = np.zeros((1, MaxIteration))  # 用于记录每一次迭代中的局部最优解
    RouteRecordMax = np.zeros((1, MaxIteration))  # 用于记录每一次迭代中的最长回路长度
    RouteRecordAve = np.zeros((1, MaxIteration))  # 用于记录每一次迭代中的蚂蚁周游的平均路径长度
    BestRoute = []  # 用于记录最优环游路线中城市的经过顺序
 
    # 执行算法，绘制最优路径图
    ACO_TCP(City_X, City_Y)