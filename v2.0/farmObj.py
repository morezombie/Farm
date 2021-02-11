import numpy as np
import matplotlib.pyplot as plt
import farmCfg
import sys

config = farmCfg.Config()

class Animal(object):
    global config
    age_mon = 0.      # age
    isMale = False    # gender
    feed_month = 0    # feeding cost per month
    observer = None   # the money observer
    matured_price = 0 # selling or buying price for big one
    newborn = False
    def __init__(self, age_month):
        if age_month == 0:
            self.newborn = True
        self.age_month = age_month
    def register(self, observer):
        self.observer = observer
    def growup(self):
        if self.newborn:    # skip its first grow
            self.newborn = not self.newborn
            return
        self.age_month += 1
        if self.observer:
            self.observer.onGrowConsume(self.feed_month)
    def estimate(self):
        if self.isCub():
            gold = config.price_cub
        else:
            gold = self.matured_price
        return gold
    def pawn(self, pack, forced):  # sold for gold
        pass
    def getSick(self, pack):
        pass
    def isCub(self):
        return self.age_month < config.matured_month

class Female(Animal):
    isBabyMale = True
    isMale = False
    babe_index = -1
    feed_month = config.feed_female_month
    month_b4_birth = 0
    matured_price = config.price_matured_female 
    
    def __init__(self, age):
        Animal.__init__(self, age)
        first_birth_date = config.matured_month + config.carry_month
        if age < first_birth_date:
            self.month_b4_birth = first_birth_date - age
        else:
            self.babe_index = (age - first_birth_date) / config.birth_period_month
            self.month_b4_birth = self.babe_index * config.birth_period_month + first_birth_date - age
        
    def growup(self):
        Animal.growup(self)
        self.month_b4_birth -= 1
    
    def giveBirth(self, pack, observer):
        if (self.month_b4_birth > 0):
            # print("%d month to give birth" % self.month_b4_birth)
            return
        if self.isBabyMale:
            newborn = Male(0)
            gender = "male"
        else:
            newborn = Female(0)
            gender = "female"
        newborn.register(observer)
        pack.append(newborn)
        print("Congrats! newborn " + gender + " Cub and pack size goes to ", len(pack))
        self.isBabyMale = not self.isBabyMale
        self.month_b4_birth = config.birth_period_month
        self.babe_index += 1

    def pawn(self, pack, forced = False):
        if not forced and self.age_month < config.max_keeping_month:
            return 0
        gold = self.estimate()
        pack.remove(self)    # how
        if self.observer:
            self.observer.onSell(gold)

class Male(Animal):
    isMale = True
    feed_month = config.feed_male_month
    matured_price = config.price_matured_male 
    
    def pawn(self, pack, forced = False):
        if not forced and self.isCub():
            return 0
        gold = self.estimate()
        pack.remove(self)    # how
        if self.observer:
            self.observer.onSell(gold)

class CounterClerk(object):
    money = 0
    month = 0
    annual_wealth = []
    annual_increase = []
    annual_matured_female = []
    annual_cub = []
    def onBuyMedicine():
        pass
    def onGrowConsume(self, gold):
        self.money -= gold
        print("[feeding] cash -%d, $%d" % (gold, self.money))
    def onBuy(self, gold):
        self.money -= gold
        print("[buying] cash -%d, $%d" % (gold, self.money))
    def onSell(self, gold):
        self.money += gold
        print("[selling] cash +%d, $%d" % (gold, self.money))
    def __init__(self, initmoney = 0):
        self.money = initmoney
    def estimate(self, pack):
        gold = 0
        male = 0
        female = 0
        cub = 0
        for obj in pack:
            # money aspect
            gold += obj.estimate()
            # animal statistics
            print("[estate] animal age:%d price %d" % (obj.age_month, obj.estimate()))
            if obj.isCub():
                cub += 1
            elif obj.isMale:
                male += 1
            else:
                female += 1
        self.annual_matured_female.append(female)
        self.annual_cub.append(cub)
        return gold
    def syncWallClock(self, month):
        print("At the end of Month", month)
        self.month = month
    def book(self, pack):
        if (self.month % 12 == 0):
            estate = self.estimate(pack)
            wealth = self.money + estate
            if self.annual_wealth:
                increase = wealth - self.annual_wealth[-1]
            else:
                increase = 0
            self.annual_wealth.append(wealth)
            self.annual_increase.append(increase)
            print("[estate] money %d and estate %d makes it %d" % (self.money, estate, wealth))
    def show(self):
        # TODO drawing annual data
        print('wealth: ', self.annual_wealth)
        print('increase: ', self.annual_increase)
        print('cub: ', self.annual_cub)
        print('female: ', self.annual_matured_female)
        
        years = len(self.annual_cub)
        fig = plt.figure(figsize=(16,8))
        numFig = fig.add_subplot(1,2,1)
        numFig.plot(range(years), self.annual_matured_female, color='black', label='grow-up female')
        numFig.plot(range(years), self.annual_cub, color='red', label='young cub')
        numFig.legend(loc='upper left')
        numFig.set_xlabel('year')
        numFig.set_ylabel('number')
        numFig.set_title('Yearly Number Of Animal')
        plt.grid()
        ecoFig = fig.add_subplot(1,2,2)
        years = len(self.annual_wealth)
        ecoFig.plot(range(years), self.annual_wealth, color='red', label='gross profit')
        ecoFig.plot(range(years), self.annual_increase, color='blue', label='increased profit')
        ecoFig.legend(loc='upper left')
        ecoFig.set_xlabel('year')
        ecoFig.set_ylabel('profit')
        ecoFig.set_title('Yearly Profit of Animal')
        plt.grid()

class Farm(object):
    pack = []
    clerk = CounterClerk()
    def addFemale(self, age, num = 1, buying = True):
        if not buying:
            gold = 0
        if age >= config.matured_month:
            gold = config.price_matured_female
        else:
            gold = config.price_cub
        for i in range (0, num):
            obj = Female(age)
            obj.register(self.clerk)
            self.pack.append(obj)
            self.clerk.onBuy(gold)

    def run(self, month):
        self.clerk.syncWallClock(0)
        self.clerk.book(self.pack)
        for m in range (1, month + 1):
            self.clerk.syncWallClock(m)
            for obj in self.pack:
                obj.growup()
                if not obj.isMale:
                    obj.giveBirth(self.pack, self.clerk)
                obj.pawn(self.pack)
                obj.getSick(self.pack)
            self.clerk.book(self.pack)
        self.clerk.show()
        print('done')