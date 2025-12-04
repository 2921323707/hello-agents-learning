""""
题目：基于蚁群算法的TSP
姓名：Rainbook
最终修改时间：2023.12.30
"""
import numpy as np
import matplotlib.pyplot as plt
import time
 
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 使用微软雅黑字体
plt.rcParams['axes.unicode_minus'] = False  # 处理负号显示异常
 
 
# 初始城市位置的散点图
def GetDistanceMatrix(X,Y,CityCount):
    plt.figure(1)
    plt.plot(X, Y, 'r''o')
    plt.xlabel("横坐标", fontproperties="Simhei")
    plt.ylabel("纵坐标", fontproperties="Simhei")
    plt.title("城市分布散点图", fontproperties="Simhei")
    # plt.show()
    # 生成一个方阵作为任意两城市之间的距离矩阵
    DistanceMatrix = np.zeros((CityCount,  CityCount))
    # 通过逐行逐列遍历的方式填充矩阵元素（第i行第j列的元素表示i和j两个城市之间的距离）
    for row in range(CityCount):
        for col in range(CityCount):
            DistanceMatrix[row,col]=((X[0,row]-X[0,col])**2+(Y[0,row]-Y[0,col])**2)**0.5
    # 将进行了填充后的距离矩阵返回输出
    return DistanceMatrix
 
 
# 算法实现
def ACO_TCP(X , Y):
    # 根据城市个数生成城市距离矩阵
    DistanceMatrix=GetDistanceMatrix(X,Y,CityCount)
 
    ##开始计时 ##
    start=time.time()
 
    # 根据蚂蚁的数量为每一只蚂蚁随机分配初始城市
    AntPlaceVector = np.random.randint(0,CityCount-1,(1,AntCount))
 
    # 接着生成初始信息素矩阵
    # 首先随机生成一条周游路线以初始化每条边上的信息素
    RandomRoute = np.random.permutation(np.arange(CityCount))
    TempLength = 0
    for i in range(CityCount-1):
        TempLength += DistanceMatrix[RandomRoute[i],RandomRoute[i+1]]
    TempLength += DistanceMatrix[RandomRoute[0],RandomRoute[CityCount-1]]
    PheromoneMatrix = np.full((CityCount,CityCount),1/TempLength)
    # 对角线上的元素初始化为零
    for i in range(CityCount):
        PheromoneMatrix[i, i] = 0
 
    # 循环迭代部分
    for iteration in range(MaxIteration):
        print("迭代次数：%s" % (iteration + 1))
        # 创建一个禁忌表，用双重列表的形式进行定义
        TabooList = []
        # 首先定义禁忌表中的每一个元素都是一个列表，表示某一只蚂蚁的禁忌表
        for i in range(AntCount):
            TabooList.append([])
        # 接下来对禁忌表中进行第一轮内容填充
        for i in range(AntCount):
            TabooList[i].append(AntPlaceVector[0, i])
        # 首先求出每一轮迭代中每一只蚂蚁进行下一目的地选择的概率向量
        for i in range(CityCount-1):
            for ant in range(AntCount):
                ProbilityVector = np.zeros((1, CityCount))
                for city in range(CityCount):
                    if city in TabooList[ant]:
                        continue
                    TempPheromone = PheromoneMatrix[TabooList[ant][len(TabooList[ant]) - 1], city]
                    TempNegDistance = 1 / DistanceMatrix[TabooList[ant][len(TabooList[ant]) - 1], city]
                    ProbilityVector[0, city] = (TempPheromone ** Alpha) * (TempNegDistance ** Beta)
                Pro_Sum = np.sum(ProbilityVector, axis=1)
                ProbilityVector = ProbilityVector / Pro_Sum
                # 求出概率向量后使用逐次轮盘法进行抽签得到每只蚂蚁下一次所到达的城市
                Next_City = np.random.choice(np.arange(0, CityCount), (1, 1), p=ProbilityVector[0, :])[0, 0]
                TabooList[ant].append(Next_City)
        # 至此已经得到了某一轮迭代中每一只蚂蚁的行进路线，用一个列表表示，接下来分别计算每只蚂蚁的周游路线的长度
        RouteLengths=[]
        for ant in range(AntCount):
            TempRouteLength=0
            for i in range(CityCount-1):
                Route=DistanceMatrix[TabooList[ant][i],TabooList[ant][i+1]]
                TempRouteLength+=Route
            TempRouteLength+=DistanceMatrix[TabooList[ant][0],TabooList[ant][len(TabooList[ant])-1]]
            RouteLengths.append(TempRouteLength)
        # 记录此时的局部最优解
        BestRoute = TabooList[RouteLengths.index(min(RouteLengths))]
        RouteRecordMin[0, iteration] = min(RouteLengths)
        RouteRecordMax[0, iteration] = max(RouteLengths)
        RouteRecordAve[0, iteration] = sum(RouteLengths)/len(RouteLengths)
        BestRoute=TabooList[RouteLengths.index(min(RouteLengths))]
 
        # 接下来更新信息素矩阵
        New_PheromoneMatrix = np.zeros((CityCount,CityCount))
        for row in range(CityCount):
            for col in range(row+1):
                if row == col:
                    break
                NewInfo = 0
                # 如果某只蚂蚁经过了该条路径，则会增加该路径上的信息素
                for ant in range(AntCount):
                    for i in range(CityCount-1):
                        if TabooList[ant][i] == row and TabooList[ant][i + 1] == col:
                            NewInfo += (Q / RouteLengths[ant])
                    if TabooList[ant][CityCount - 1] == row and TabooList[ant][0] == col:
                        NewInfo += (Q / RouteLengths[ant])
                    if TabooList[ant][CityCount - 1] == col and TabooList[ant][0] == row:
                        NewInfo += (Q / RouteLengths[ant])
                New_PheromoneMatrix[row, col] = (1-VolatilizationRate)*PheromoneMatrix[row, col]+VolatilizationRate*NewInfo
                New_PheromoneMatrix[col, row] = (1-VolatilizationRate)*PheromoneMatrix[row, col]+VolatilizationRate*NewInfo
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
    print("最短环游路径的长度为：", [0, MaxIteration-1])
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