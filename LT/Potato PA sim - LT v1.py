# -*- coding: utf-8 -*-
"""
Created on Sat 3 July 2021

@author: Potato
"""
import random
import datetime
import numpy as np

import pickle
import os
import matplotlib.pyplot as plt
#import matplotlib.ticker as mtick
import json

class simMonthly(object):
    
    def __init__(self,days,initEMP, extraE, aidCom, banner, prio, collect = 'all', resetPool = 'False'):
        self.days, self.EMP, self.extraE, self.aidCom = days, initEMP, extraE, aidCom
        self.prio = prio
        self.m1 = "Mook1*"
        self.m2 = "Mook2*"
        self.fillBanner(banner, collect)
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
        #Brings simulation forward 12 hours and progresses time-gated systems
        self.t += 0.5
        if self.refreshCD > 0: self.refreshCD -= 0.5
        if self.EMP < 14 and self.t != self.days: self.EMP += 1
        
    def fillBanner(self, bn, c):
        #Fills empty space in the banner with nameless units
        # 1 3*, 21 2*, 78 1*
        if self.m1 not in bn: 
            self.rarityCount = [0,0,0]
            for i in bn:
                self.rarityCount[bn[i]["Rarity"]-1] += bn[i]["Count"]
                if c == 'all' and bn[i]["Rarity"] == 3: bn[i]["Priority"] = 5
            bn[self.m2] = {"Count":21 - self.rarityCount[1], "Rarity": 2, "Desire": 0, "Priority": 2}
            bn[self.m1] = {"Count":78 - self.rarityCount[0], "Rarity": 1, "Desire": 0, "Priority": 1}
        
        self.b = bn
            
    def setPool(self):
        #Create a pool list based on the banner information
        #Also creates a smaller pool of priority units that will be used to evaluate if the goal is attained
        pool = []
        plist = []
        for i in self.b:
            pool.extend([i]*self.b[i]["Count"])
            if self.b[i]["Priority"] >= self.prio:
                plist.extend([i]* self.b[i]["Desire"])
        assert len(pool) == 100
        self.pool = pool
        self.pList = plist
        
    def refresh(self):
        #Supply a new set of units for the field
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
        #Simulate an aid commission, pulling a random unit directly from the pool
        #Whaling occurs after the tickets are expended but the goal has not been attained
        a = random.choice(self.pool)
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
        self.monthEndRSC["Impulse"].append(self.impulse-1)
        self.monthEndRSC["XImpulse"].append(self.extraImpulse)
        self.monthEndRSC["AidCom"].append(self.aidCom)
        
        self.impulse = emp
        self.extraImpulse = xmp
        self.aidCom = svr
        if mn+1 < len(self.b):
            self.extraImpulse += self.p["MonthlyExtraImpulse"][(mn+1)%len(self.p["MonthlyExtraImpulse"])]
            self.aidCom += self.p["MonthlyAidCommisions"][(mn+1)%len(self.p["MonthlyAidCommisions"])]
        
        
    def LTsim(self):
        # Run banner simulations, passing forward capture related resources to the following cycle
        for mn in range(self.blen):
            self.mCap = simMonthly(self.p["Duration"],self.impulse,self.extraImpulse,self.aidCom, self.b[mn], self.prio, self.collect, self.poolReset)
            a,b,c,d,e = self.mCap.runSim()
            self.deposit(d, e)
            self.upkeep(a, b, c, mn)
        return self.armoury, self.whalemoury, self.monthEndRSC, self.debt

if __name__ == '__main__':
    t1 = datetime.datetime.now()
    dirfils = os.listdir()
    
    with open('Params.json') as f:
    #Import settings and whatever junk from json file
        settingsIn = json.load(f)
        nSKK = settingsIn["nSKK"]
        CaptureParams = settingsIn["CaptureParams"]
        Banners = settingsIn["Banners"]
        DataDisplay = settingsIn["DataDisplay"]
    xLen = list(range(len(Banners)))
    Armoury = {}
    Whaling = {}
    Wallet = []
    endRSC = {"Impulse":[0]*len(Banners), "XImpulse": [0]*len(Banners), "AidCom":[0]*len(Banners)}
        
    for i in range(nSKK):
        if i % 2500 == 0: print("Progressing, trial number {}".format(i))
        iskk = SKK( params = CaptureParams,banners = Banners)
        a,b,c,d = iskk.LTsim()
        for j in b:
            if j in Whaling: Whaling[j].append(b[j])
            else: Whaling[j] = [b[j]]
        for i in a:
            if i in Armoury: Armoury[i].append(a[i])
            else: Armoury[i] = [a[i]]
            if i not in Whaling: Whaling[i] = []
        Wallet.append(d)
        for k in endRSC:
            for h in xLen:
                endRSC[k][h] =+ c[k][h]
    
    
    with open("Armoury.pickle",'wb') as f1: pickle.dump(Armoury, f1)
    with open("Whale additions.pickle",'wb') as f2: pickle.dump(Whaling, f2)
    with open("End RSC.pickle",'wb') as f3: pickle.dump(endRSC, f3)
    
    plt.rc('axes', titlesize=26)
    plt.rc('axes', labelsize=22)
    plt.rc('xtick', labelsize=20)
    plt.rc('ytick', labelsize=20)
    
    px = 1/plt.rcParams['figure.dpi']
    fig, axs = plt.subplots(2,2,figsize=(DataDisplay["ImageSize"]["W"]*px,DataDisplay["ImageSize"]["H"]*px))
    fig.suptitle("Extended time SF Capture simulation\n{} banner periods, {} simulated players".format(len(Banners), nSKK), fontsize = 30)

    #Proportion of capture of ringleaders
    #Volume of capture for other units
    aList, wList, oList, rList, eList = [[],[]],[[],[]],[],[],[]
    for n in Banners:
        for p in n:
            if n[p]["Rarity"] == 3 and p not in rList: rList.append(p)
            elif p not in eList: eList.append(p)
    for m in rList:
        aList[0].append(np.round(sum(Armoury[m])/nSKK,2))
        wList[0].append(np.round(sum(Whaling[m])/nSKK,2))
    for h in eList:
        aList[1].append(np.round(sum(Armoury[h])/nSKK,2))
        wList[1].append(np.round(sum(Whaling[h])/nSKK,2))
    b4 = axs[0,0].bar(rList,aList[0],label = 'Standard capture')
    b5 = axs[0,0].bar(rList,wList[0],label = 'Whale capture',bottom = aList[0])
    axs[0,0].legend(loc = 4,fontsize = 18)
    axs[0,0].set_xticklabels(labels = rList, fontsize = 14, rotation = 65)
    axs[0,0].bar_label(b4, fontsize = 18, label_type = 'center')
    axs[0,0].bar_label(b5, fontsize = 18, label_type = 'center')
    b6 = axs[1,1].bar(eList,aList[1],label = 'Standard capture')
    b7 = axs[1,1].bar(eList,wList[1],label = 'Whale capture',bottom = aList[1])
    axs[1,1].legend(loc = 2,fontsize = 18)
    axs[1,1].bar_label(b6, fontsize = 18, label_type = 'center')
    axs[1,1].bar_label(b7, fontsize = 18, padding = 4)
    
    #Remaining resources
    barW = DataDisplay["GroupBarWidth"]
    xb = np.arange(len(xLen))
    b1 = axs[0,1].bar(xb-barW,endRSC["Impulse"], width = barW, label = "Impulse")
    b2 = axs[0,1].bar(xb,endRSC["XImpulse"], width = barW, label = "Extra impulses")
    b3 = axs[0,1].bar(xb+barW,endRSC["AidCom"], width = barW, label = "Aid commissions")
    axs[0,1].set_xticks(xLen)
    axs[0,1].set_title("Remaining resources on month end")
    axs[0,1].legend(loc = 2,fontsize = 18)
    axs[0,1].bar_label(b1, padding = 3,fontsize=10)
    axs[0,1].bar_label(b2, padding = 1,fontsize=10)
    axs[0,1].bar_label(b3, padding = 2,fontsize=10)

    #Whaling histogram
    wbins = DataDisplay["WhaleBins"]
    axs[1,0].hist(Wallet, bins = int(np.ceil(max(Wallet)/wbins)))
    axs[1,0].set_title("Total gem expense to complete goal")
    axs[1,0].tick_params(axis='both', which='major', labelsize=18)
    axs[1,0].set_ylabel("Count")
    axs[1,0].set_xlabel("#SKK, bin size {} gems".format(wbins))
    
    fig.tight_layout()
   
    t2 = datetime.datetime.now()
    dt = t2-t1
    dtm = int(dt.seconds/60)
    dts = dt.seconds % 60
    plt.text(-0.08,1.04,'Runtime: {}m{}s'.format(dtm,dts),horizontalalignment='left',
             verticalalignment='bottom', fontsize = 16,  transform = axs[0,0].transAxes)
    print("Time elapsed: {}m{}s".format(dtm,dts))
    
    fig.savefig('Figure {}.png'.format(str(t2)[:-7].replace(':','')))

    
    