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
    def __init__(self, age_month):
        self.age_month = age_month
    def register(self, observer):
        self.observer = observer
    def growup(self):
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
        print("feeding, cash -%d, $%d" % (gold, self.money))
    def onBuy(self, gold):
        self.money -= gold
        print("buying, cash -%d, $%d" % (gold, self.money))
    def onSell(self, gold):
        self.money += gold
        print("selling, cash +%d, $%d" % (gold, self.money))
    def __init__(self, initmoney = 0):
        self.money = initmoney
        self.annual_wealth.append(initmoney)
    def estimate(self, pack):
        gold = 0
        male = 0
        female = 0
        cub = 0
        for obj in pack:
            # money aspect
            gold += obj.estimate()
            # animal statistics
            print("obj age:%d price %d" % (obj.age_month, gold))
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
        self.month = month
    def book(self, pack):
        if (self.month % 12 == 0):
            estate = self.estimate(pack)
            wealth = self.money + estate
            print("money %d and estate %d makes it %d" % (self.money, estate, wealth))
            increase = wealth - self.annual_wealth[-1]
            self.annual_wealth.append(wealth)
            self.annual_increase.append(increase)
    def show(self):
        # TODO drawing annual data
        print('wealth: ', self.annual_wealth)
        print('increase: ', self.annual_increase)
        print('cub: ', self.annual_cub)
        print('female: ', self.annual_matured_female)

class Farm(object):
    pack = []
    clerk = CounterClerk()
    def addFemale(self, age):
        obj = Female(age)
        obj.register(self.clerk)
        self.pack.append(obj)

    def run(self, month):
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