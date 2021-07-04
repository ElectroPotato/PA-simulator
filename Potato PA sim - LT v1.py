# -*- coding: utf-8 -*-
"""
Created on Sat 3 July 2021

@author: Potato
"""
import random
import datetime
import numpy as np

#import pickle
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import json

class simMonthly(object):
    
    def __init__(self,days,initEMP, extraE, aidCom, banner, prio, collect = 'all', resetPool = 'False'):
        self.days, self.EMP, self.extraE, self.aidCom = days, initEMP, extraE, aidCom
        self.prio = prio
        self.m1 = "Mook1"
        self.m2 = "Mook2"
        self.banner = banner
        self.fillBanner(self.banner, collect)
        self.setPool()
        self.refresh()
        self.t = 0
        self.claims = []
        self.wclaims = []
        self.e = 'e'
        self.witness = 0
        self.whaleAid = 0
        self.RL = False
        self.goal = False
        self.e = 'e'
        self.resetPool = resetPool
        
    def timestep(self):
        self.t += 0.5
        if self.refreshCD > 0: self.refreshCD -= 0.5
        if self.EMP < 14 and self.t != self.days: self.EMP += 1
        
    def fillBanner(self, bn, c):
        self.rarityCount = [0,0,0]
        for i in bn:
            self.rarityCount[bn[i]["Rarity"]-1] += bn[i]["Count"]
            if c == 'all' and bn[i]["Rarity"] == 3: bn[i]["Priority"] = 5
        bn[self.m2] = {"Count":21 - self.rarityCount[1], "Rarity": 2, "Priority": 2}
        bn[self.m1] = {"Count":78 - self.rarityCount[0], "Rarity": 1, "Priority": 1}
        self.b = bn
            
    def setPool(self):
        pool = []
        db.write("\nCALL TO SET POOL\n")
        plist = []
        for i in self.b:
            pool.extend([i]*self.b[i]["Count"])
            if self.b[i]["Priority"] >= self.prio:
                plist.extend([i])#* self.b[i]["Count"])
        self.pool = pool
        self.pList = plist
        
    def refresh(self):
        if len(self.pool) > 3:
            self.field = random.sample(self.pool,3)
        else: self.field = self.pool
        self.refreshCD = 3
        
    def rPool(self):
        self.setPool()
        self.refresh()
        
    def whale(self):
        self.svarog(whale = True)
        
    def svarog(self, whale = False):
        a = random.choice(self.pool)
        db.write("{} {} aid {} pool {} {} goal\n".format(whale, self.aidCom, len(self.pool), a, self.goal))
        if whale: 
            self.wclaims.append(a)
            self.whaleAid += 1
        else: 
            self.claims.append(a)
            self.aidCom -= 1
        if a in self.field:
            if random.randint(1,self.pool.count(a)) == 1:
                self.field.remove(a)
                self.refillField()
        if self.b[a]["Rarity"] == 3: 
            self.RL = True
            self.witness += 1
            if self.resetPool: self.rPool()
        self.pool.remove(a)
        assert self.aidCom >= 0
        
    def capture(self, doll, e = 'e'):
        db.write("{}, {} field, {} pool, \tday {}\n".format(doll,len(self.field),len(self.pool),self.t))
        db.write("\t{}, {} extra, {} aid {} goal\n".format(self.EMP,self.extraE, self.aidCom, self.goal))
        #Attempt a capture operation, at the cost of regular or extra impulse
        #Determine rarity of unit, apply capture chance to remove from pool and add to monthly gains
        #Remove unit from field and replace
        if e == 'e': self.EMP -= 1
        else: self.extraE -= 1
        if self.b[doll]["Rarity"] == 1:
            self.field.remove(doll)
            self.pool.remove(doll)
            self.claims.append(doll)
            self.refillField()
        elif self.b[doll]["Rarity"] == 2:
            c = random.choice([1,0])
            self.field.remove(doll)
            if c == 1:
                self.pool.remove(doll)
                self.claims.append(doll)
            self.refillField()
        elif self.b[doll]["Rarity"] == 3:
            self.witness += 1
            c = random.choice([1,0,0,0])
            self.field.remove(doll)
            if c == 1:
                self.pool.remove(doll)
                self.claims.append(doll)
                self.RL = True
            self.refillField()
            if c == 1 and self.resetPool: self.rPool()

        assert self.EMP >= 0
        assert self.extraE >= 0
    
    def refillField(self):
        # Add a new unit to the field after one is taken away, if there are any available in the pool
        q = self.pool.copy()
        for i in self.field: q.remove(i)
        if len(q) > 0:
            self.field.append(random.choice(q))
        assert len(self.field) <= 3
        
    def maintain(self):
        #Ensures the number of available units on the field does not exceed the number of the same unit in the pool
        for i in self.field.copy():
            if self.field.count(i) > self.pool.count(i):
                self.field.remove(i)
                self.refillField()
        #Sort field by unit priority
        self.field.sort(key = lambda n: self.b[n]["Priority"], reverse = True)
        #Check if the goal of capturing (1 or all) of units of at least self.prio is achieved
        if not self.goal and (self.days - self.t) <= 7:
            k = 0
            w = (self.claims + self.wclaims).copy()
            for u in self.pList:
                if u in w:
                    w.remove(u)
                    k += 1
            if len(self.pList) == k: self.goal = True
    
    def rarityInField(self, r):
        # Determine whether a unit of given rarity is present in the field
        for i in self.field:
            if self.b[i]["Rarity"] == r: return True
        return False
    
    def priorityInField(self,p):
        # Determine whether a unit of given priority is present in the field
        for i in self.field:
            if self.b[i]["Priority"] >= p: return True
        return False
    
    def runSim(self):
        while self.t <= self.days:
            self.maintain()
            if self.t != self.days:
                if self.EMP == 0 and self.refreshCD == 0 and not self.priorityInField(3) and not self.rarityInField(1):
                    self.refresh()
                elif self.EMP == 0: 
                    self.timestep()
                elif self.priorityInField(3):
                    self.capture(self.field[0])
                elif self.goal and ((self.days-self.t)*2 >= self.EMP):
                    self.timestep()
                elif self.rarityInField(1) and not self.goal:
                    self.capture(self.field[-1])
                elif self.refreshCD == 0:
                    self.refresh()
                elif self.EMP < 14:
                    self.timestep()
                elif len(self.field) > 0:
                    self.capture(self.field[0])
                else: self.timestep()
                    
            elif self.t == self.days:
                if self.EMP == 0: self.e = 'x'
                if len(self.pool) == 0 or self.goal: self.timestep()
                elif self.priorityInField(3) and (self.EMP > 0 or self.extraE > 0):
                    self.capture(self.field[0],self.e)
                elif len(self.pool) <= 4 and self.aidCom > 0 and len(self.pool) > 0:
                    self.svarog()
                elif self.rarityInField(1) and self.EMP > 0:
                    self.capture(self.field[-1])
                elif self.refreshCD == 0:
                    self.refresh()
                elif self.rarityInField(2) and self.EMP > 0:
                    self.capture(self.field[0])
                elif self.rarityInField(1) and self.extraE > 0:
                    self.capture(self.field[-1],'x')
                elif self.rarityInField(2) and self.extraE > 0:
                    self.capture(self.field[0],'x')
                elif self.aidCom > 0 and len(self.pool) > 0 and not self.goal:
                    self.svarog()
                elif self.aidCom == 0 and len(self.pool) > 0 and not self.goal:
                    self.whale()
                else: self.timestep()
        return (self.EMP, self.extraE, self.aidCom, self.claims, self.wclaims)

class SKK(object):
    
    def __init__(self, params, banners):
        self.p = params
        self.b = banners
        self.blen = len(self.b)
        self.prio = self.p["PriorityFocus"]
        self.impulse = self.p["InitialEMP"]
        self.extraImpulse = self.p["MonthlyExtraImpulse"][0]
        self.aidCom = self.p["MonthlyAidCommisions"][0]
        self.poolReset = self.p["PoolResetOnRLCap"]
        self.armoury = {} #Units captured using standard means
        self.whalemoury = {} #Units that would be added using whaled aid commission tickets
        self.debt = 0 #160 gems per aid commission
        self.collect = 'all'
        self.monthEndRSC = {"Impulse":[], "XImpulse": [], "AidCom":[]} #Random metrics
        
    def deposit(self, catches, overFishing):
        # Records the captures of the month into SKK's display case
        for i in catches:
            if i in self.armoury.keys(): self.armoury[i] += 1
            else: self.armoury[i] = 1
        # Records the captures of the month that involved money into a different display case
        for j in overFishing:
            self.debt += 160
            if j in self.whalemoury.keys(): self.whalemoury[j] += 1
            else: self.whalemoury[j] = 1
        
    def upkeep(self,emp,xmp,svr, mn):
        # Updates the impulses and aid commisions available to be used next month
        self.impulse = emp
        self.extraImpulse = xmp
        self.aidCom = svr
        if mn+1 < len(self.b):
            self.extraImpulse += self.p["MonthlyExtraImpulse"][(mn+1)%len(self.p["MonthlyExtraImpulse"])]
            self.aidCom += self.p["MonthlyAidCommisions"][(mn+1)%len(self.p["MonthlyAidCommisions"])]
        self.monthEndRSC["Impulse"].append(self.impulse)
        self.monthEndRSC["XImpulse"].append(self.extraImpulse)
        self.monthEndRSC["AidCom"].append(self.aidCom)
        
    def LTsim(self):
        # Run banner simulations, passing forward capture related resources to the following cycle
        for mn in range(self.blen):
            db.write("TRIAL MONTH {}\n\n".format(mn))
            self.mCap = simMonthly(self.p["Duration"],self.impulse,self.extraImpulse,self.aidCom, self.b[mn], self.prio, self.collect, self.poolReset)
            a,b,c,d,e = self.mCap.runSim()
            self.deposit(d, e)
            self.upkeep(a, b, c, mn)
        return self.armoury, self.whalemoury, self.monthEndRSC, self.debt

if __name__ == '__main__':
    t1 = datetime.datetime.now()
    Armoury = {}
    Whaling = {}
    Wallet = []
    random.seed(1)
    global db
    with open("debuglog.txt",'w') as db:
        
        with open('Params.json') as f:
            settingsIn = json.load(f)
            nSKK = settingsIn["nSKK"]
            CaptureParams = settingsIn["CaptureParams"]
            Banners = settingsIn["Banners"]
            
        for i in range(nSKK):
            if i % 2500 == 0: print("Progressing, trial number {}".format(i))
            db.write("SKK #{}\n".format(i))
            iskk = SKK( params = CaptureParams,banners = Banners)
            a,b,c,d = iskk.LTsim()
            for i in a:
                if i in Armoury: Armoury[i].append(a[i])
                else: Armoury[i] = [a[i]]
            for j in b:
                if j in Whaling: Whaling[j].append(b[j])
                else: Whaling[j] = [b[j]]
            Wallet.append(d)
            del iskk

'''
    plt.rc('font', size=26)
    plt.rc('axes', titlesize=24)
    plt.rc('axes', labelsize=20)
    plt.rc('legend', fontsize=12)
    
    fig, (ax1,ax2) = plt.subplots(2,figsize=(10,15))
    fig.suptitle("{} initial EMP\n{} trials per point".format(b,nTrials))
    
    ax3 = ax1.twinx()
    ax3.set_ylim(ymin = 0)
    ax1.set_xticks(list(range(0,c,2)))
    ax2.set_xticks(list(range(0,c,2)))
    
    ax1.set_title("Capture costs")
    ax1.set_ylabel("Impulse to capture")
    ax3.set_ylabel("Aid to capture")
    ax2.set_title("Capture rate")
    ax1.set_xlabel("Surplus impulse")
    ax2.set_xlabel("Surplus impulse")
    for k in range(d):
        ax1.plot(countE[k,:], label = "{} aid".format(k))
        ax3.scatter(list(range(c)), countA[k,:], label = "{} aid".format(k), s = 50)
        ax2.plot(countC[k,:], label = "{} aid".format(k))
        
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=None))
    ax2.legend()
    ax1.legend()
    
    fig.tight_layout()
    t2 = datetime.datetime.now()
    
    dt = t2-t1
    dtm = int(dt.seconds/60)
    dts = dt.seconds % 60
    plt.text(-0.08,1.04,'Runtime: {}m{}s'.format(dtm,dts),horizontalalignment='left',
             verticalalignment='bottom', fontsize = 16,  transform = ax1.transAxes)
    print("Time elapsed: {}m{}s".format(dtm,dts))
    
    fig.savefig('Figure {}.png'.format(str(t2)[:-7].replace(':','')))


'''    
    #t3 = datetime.datetime.now()
    #print("Time elapsed: {} seconds".format((t3-t1).seconds))

    
    