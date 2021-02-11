#coding=utf-8
import sys
import numpy as np
from numpy import array as array
import matplotlib.pyplot as plt

np.set_printoptions(precision=2)

class CattleFarm:
    price = 2
    seize = 1.2
    feed = 0.4
    cow = array([0,1])
    cub = array([1,0])
    newborn = array([])
    ox = array([0,0])
    cost = array([0, feed])
    profit = array([0,price - feed])
    delta = profit
    year = 0

    def calcFromConfig(self, cow, cub, year):
        if year < 0:
            return
        self.year = year
        self.cow = array([cow, cow + cub/2.])
        self.cub = array([cub, 0])
        self.newborn = array([0, cow])
        self.ox = array([0, cub/2.])
        self.cost = array([0, (cow + cub) * self.feed])
        self.profit = array([0, (cow + cub) * (self.price - self.feed)])
        self.delta = self.profit
        for i in range(2, year):
            self.cow = np.append(self.cow, self.cow[i-1] + (self.cub[i-2]/2.))
            self.cub = np.append(self.cub, self.newborn[i-1])
            self.newborn = np.append(self.newborn, self.cow[i-1])
            self.ox = np.append(self.ox, self.ox[i-1] + self.cub[i-2]/2.)
            c = (self.cow[i-1] + self.cub[i-1] + self.newborn[i-1]) * self.feed
            self.cost = np.append(self.cost, self.cost[i-1] + c)
            self.profit = np.append(self.profit, (self.ox[i] + self.cow[i]) * self.price + (self.cub[i] + self.newborn[i]) * self.seize - self.cost[i] - self.seize)
            self.delta = np.append(self.delta, self.profit[i] - self.profit[i-1])
        self.show()
        
    def calc(self, year):
        if year < 0:
            return
        self.year = year
        for i in range(2, year):
            self.cow = np.append(self.cow, self.cow[i-1] + (self.cub[i-1]/2.))
            self.cub = np.append(self.cub, self.cow[i-1])
            self.ox = np.append(self.ox, self.ox[i-1] + self.cub[i-1]/2.)
            c = (self.cow[i-1] + self.cub[i-1]) * self.feed
            self.cost = np.append(self.cost, self.cost[i-1] + c)
            self.profit = np.append(self.profit, (self.ox[i] + self.cow[i]) * self.price + self.cub[i] * self.seize - self.cost[i] - self.seize)
            self.delta = np.append(self.delta, self.profit[i] - self.profit[i-1])
        self.show()

    def show(self):
        fig = plt.figure(figsize=(16,8))
        numFig = fig.add_subplot(1,2,1)
        numFig.plot(range(self.year), self.cow, color='black', label='growed cow')
        numFig.plot(range(self.year), self.cub, color='red', label='young cub')
        if self.newborn.size > 0:
            numFig.plot(range(self.year), self.newborn, color='blue', label='newborn cub')
        numFig.legend(loc='upper left')
        numFig.set_xlabel('year')
        numFig.set_ylabel('number')
        numFig.set_title('Increasement of Cattle')
        plt.grid()
        
        ecoFig = fig.add_subplot(1,2,2)
        ecoFig.plot(range(self.year), self.profit, color='red', label='pure profit')
        ecoFig.plot(range(self.year), self.delta, color='blue', label='single year profit')
        ecoFig.legend(loc='upper left')
        ecoFig.set_xlabel('year')
        ecoFig.set_ylabel('profit')
        ecoFig.set_title('Profig of Cattle')
        
        plt.grid()
        print("sing:",self.delta)
        print("prof:",self.profit)

    
if __name__ == '__main__':
    year = int(sys.argv[1])
    CattleFarm.calc(year)
    print("done")
