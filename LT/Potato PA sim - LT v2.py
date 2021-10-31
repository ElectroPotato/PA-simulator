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
import matplotlib.ticker as mticker
import json

class simMonthly(object):
    """
    An individual banner simulation, typically 28 days in length.
    Recieves information on available units during that banner.
    Recieves information on what resources the player has available.
    """
    def __init__(self,days: int, initEMP: int, extraE: int, aidCom: int, 
                 banner: dict, prio: int, collect: bool = True, 
                 resetPool: bool = 'False', desireLim: int = 1, 
                 RLprio: int = 7, rat1: float = 0.46):
        self.days, self.EMP, self.extraE, self.aidCom = days, initEMP, extraE, aidCom
        self.prio = prio
        self.RLprio = RLprio
        self.m1 = "Mook1*" #Label for nameless 1* units. Redundant after filling full banner.
        self.m2 = "Mook2*" #Label for nameless 2* units. redundant after filling full banner.
        self.RLname = "Potato"
        self.dlim = desireLim
        self.rat1 = rat1
        self.fillBanner(banner, collect)
        self.setPool()
        self.refresh()
        self.t = 0
        self.claims = []
        self.wclaims = []
        self.e = 'e'
        self.witness = 0
        self.whaleAid = 0
        self.RL = False #Check if RL has been captured
        self.goal = False
        self.e = 'e'
        self.resetPool = resetPool #Bool to choose whether to reset pool on RL capture
        self.rlpsz = {"Impulse":[], "XImpulse":[], "Aid":[], "Whale":[]}#Size of pool on ringleader capture
        self.RLAction = 0 #Count of actions taken to first RL capture
        self.whaleMode = False #Check if whaling started
        
        
        
    def timestep(self):
        """Brings simulation forward 12 hours and progresses time-gated systems."""
        self.t += 0.5
        if self.refreshCD > 0: self.refreshCD -= 0.5
        if self.EMP < 14 and self.t != self.days: self.EMP += 1
        
    def fillBanner(self, bn: dict, c: str):
        """
        Fills empty space in the banner with nameless units
        1 3*
        28 2*
        71 1*
        """
        self.rarityCount = [0,0,0]
        for i in bn:
            self.rarityCount[bn[i]["Rarity"]-1] += bn[i]["Count"]
            if c and bn[i]["Rarity"] == 3: bn[i]["Priority"] = 42
            if bn[i]["Rarity"] == 3: self.RLname = i
        if self.rarityCount[1] < 28:    
            bn[self.m2] = {"Count":28 - self.rarityCount[1], "Rarity": 2, "Desire": 0, "Priority": 2}
        if self.rarityCount[0] < 71:
            bn[self.m1] = {"Count":71 - self.rarityCount[0], "Rarity": 1, "Desire": 0, "Priority": 1}
        
        self.b = bn
            
    def setPool(self, new: bool = True):
        """
        Create a pool list based on the banner information.
        Also creates a smaller pool of priority units that will be used to evaluate if the goal is attained.
        """
        if new:
            pool = []
            plist = []
            for i in self.b:
                pool.extend([i]*self.b[i]["Count"])
                if self.b[i]["Rarity"] <=2 and self.b[i]["Priority"] >= self.prio:
                    plist.extend([i] * min(self.b[i]["Desire"], self.dlim))
                if self.b[i]["Rarity"] == 3 and self.b[i]["Priority"] >= self.RLprio:
                    plist.extend([i] * self.b[i]["Desire"])
                    
            assert len(pool) == 100
            self.pool = pool
            self.poolbkp = pool
            self.pList = plist
        else:
            self.pool = self.poolbkp
        
        global glog
        if glog:
            global glof
            glof.write("{}\t{}\n".format(self.pList, self.RLname))
        
    def refresh(self):
        """Supply a new set of units for the field."""
        if len(self.pool) > 3:
            self.field = random.sample(self.pool,3)
        else: self.field = self.pool
        self.refreshCD = 3
        
    def rPool(self):
        """Pointless function used to call 2 other functions, but in 1 line."""
        self.setPool(False)
        self.refresh()
        
    def whale(self):
        """If you haven't gotten what you want, and you're out of tickets..."""
        self.whaleMode = True
        self.svarog(whale = True)
        
    def svarog(self, whale: bool = False):
        """
        Simulate an aid commission, pulling a random unit directly from the pool.
        Whaling occurs after the tickets are expended but the goal has not been attained.
        """
        if not self.RL: self.RLAction += 1
        a = random.choice(self.pool)
        if whale: 
            self.wclaims.append(a)
            self.whaleAid += 1
        else: 
            self.claims.append(a)
            self.aidCom -= 1
        if a in self.field:
            if random.randint(1, self.pool.count(a)) == 1:
                self.field.remove(a)
                self.refillField()
        if self.b[a]["Rarity"] == 3:
            self.RL = True
            if not whale: 
                self.witness += 1
                self.rlpsz["Aid"].append(len(self.pool))
            else: self.rlpsz["Whale"].append(len(self.pool))
        self.pool.remove(a)
        if self.b[a]["Rarity"] == 3 and self.resetPool: self.rPool()
        assert self.aidCom >= 0
        
    def capture(self, doll: str, e: str = 'e'):
        """
        Attempt a capture operation, at the cost of regular or extra impulse.
        Determine rarity of unit, apply capture chance to remove from pool and add to monthly gains.
        Remove unit from field and replace.
        """
        self.cdoll = doll
        global glog
        if glog:
            global glof
            glof.write("Attempt {} from {}. Pool count {}\n".format(self.cdoll, self.field, self.pool.count(doll)))
        
        if not self.RL: self.RLAction += 1
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
            #Upon attempting RL capture, increment sightings of RL if gems have not been spent
            if not self.whaleMode: self.witness += 1
            c = random.choice([1,0,0,0])
            self.field.remove(doll)
            if c == 1:
                #Upon RL capture, mark the type of impulse used.
                if e == 'e': self.rlpsz["Impulse"].append(len(self.pool))
                else: self.rlpsz["XImpulse"].append(len(self.pool))
                self.pool.remove(doll)
                self.claims.append(doll)
                self.RL = True
            self.refillField()
            #If planning to reset pool on capture, do so
            if c == 1 and self.resetPool: self.rPool()

        assert self.EMP >= 0
        assert self.extraE >= 0
    
    def refillField(self):
        """Add a new unit to the field after one is taken away, if there are any available in the pool."""
        q = self.pool.copy()
        for i in self.field: q.remove(i)
        if len(q) > 0:
            self.field.append(random.choice(q))
        assert len(self.field) <= 3
        
    def maintain(self):
        """
        Ensures the number of available units on the field does not exceed the number of the same unit in the pool.
        Check if capture goal is completed
        """
        global glog
        if glog:
            global glof
            glof.write("{} impulse, {} extra impulse, {} svarog\t Day {}, RL {}, Goal {}, Pool {}\n".format(self.EMP, self.extraE, self.aidCom, self.t, self.RL, self.goal, len(self.pool)))
        
        for i in self.field.copy():
            if self.field.count(i) > self.pool.count(i):
                self.field.remove(i)
                self.refillField()
        #Sort field by unit priority
        self.field.sort(key = lambda n: self.b[n]["Priority"], reverse = True)
        #Check if the goal of capturing (1 or all) of units of the priority list is achieved
        if not self.goal and (self.days - self.t) <= 12:
            k = 0
            w = (self.claims + self.wclaims).copy()
            for u in self.pList:
                if u in w:
                    w.remove(u)
                    k += 1
            if len(self.pList) == k: self.goal = True
            
    def splitField(self, r: int = 1) -> list:
        """
        Split off the units of specified rarity (default 1*) into a seperate list and return.
        Used to pull 1* units of interest when useful 2* or other 1* units may be present
        """
        sfield = []
        for i in self.field:
            if self.b[i]["Rarity"] == r: sfield.append(i)
        sfield.sort(key = lambda n: self.b[n]["Priority"], reverse = True)
        return sfield
    
    def ratPool(self,rar: int = 1) -> float:
        """
        Calculate and return the ratio of units of specified rarity (default 1*) to the rest of the pool
        Used to compare with the ratio needed to use aid commisions rather than extra impulses
        """
        lPool = len(self.pool)
        rCount = 0
        for i in self.pool:
            if self.b[i]["Rarity"] == rar: rCount += 1
        return round(rCount/lPool,2)
    
    def rarityInField(self, r: int, m: str = 'i') -> bool:
        """Determine whether a unit of given rarity is present in the field"""
        if m == 'i':
            for i in self.field:
                if self.b[i]["Rarity"] == r: return True
            return False
        else: 
            for i in self.field:
                if self.b[i]["Rarity"] != r: return False
            return True
        
    
    def priorityInField(self,p: int, t: str = 'g') -> bool:
        """Determine whether a unit of given priority or higher is present in the field"""
        if t == 'g':    
            for i in self.field:
                if self.b[i]["Priority"] >= p: return True
        else:
            for i in self.field:
                if self.b[i]["Priority"] == p: return True
        return False
    
    def runSim(self):# -> tuple:
        """
        Run the simulation for the specified time length.
        Series of conditional statements the actions that are to be taken.
        Exit the simulation once the timespan has passed and report information to parent SKK object.
        """
        while self.t <= self.days:
            self.maintain()
            if self.t != self.days:
                if len(self.pool) == 0: self.rPool()
                elif (self.EMP == 0 and self.refreshCD == 0 
                    and not self.priorityInField(3)): #and not self.rarityInField(1)): #Swap between refresh on no 1* or refresh if reasonable
                    self.refresh()
                
                #Test to flush 1* early using extra impulses.
                elif self.EMP == 0 and self.rarityInField(3) and self.extraE != 0 and self.RLname in self.pList and self.refreshCD == 0: self.capture(self.field[0],'x')
                #elif self.EMP == 0 and self.rarityInField(1) and self.extraE != 0 and self.RLname in self.pList and self.RLname in self.pool: self.capture(self.splitField()[0],'x')
                elif self.EMP == 0: self.timestep()
                
                elif self.priorityInField(6): #Minimum priority of RL
                    self.capture(self.field[0])
                elif self.priorityInField(3): #2* units of interest
                    self.capture(self.field[0])
                elif self.priorityInField(2,'e'): #1* units of interest
                    self.capture(self.splitField()[0])
                    
                elif self.rarityInField(1) and not self.goal:
                    self.capture(self.splitField()[0])
                
                
                elif self.refreshCD == 0:
                    self.refresh()
                elif self.goal and ((self.days-self.t)*2 < 14 - self.EMP):
                    self.timestep()
                elif self.EMP < 14:
                    self.timestep()
                elif len(self.field) > 0:
                    self.capture(self.field[0])
                else: self.timestep()
                    
            elif self.t == self.days: #End of banner, time to dump resources if desired
                if self.EMP == 0: self.e = 'x' #Change capture function to pull from extra impulses instead of regenerating
                if len(self.pool) == 0 or self.goal: self.timestep() #If the pool is empty, end the round
                
                elif (self.priorityInField(6) and (self.EMP > 0 or self.extraE > 0) 
                      and len(self.pool) >= 4): #RL in field, impulses available, pool size > 4
                    self.capture(self.field[0], self.e)
                elif self.priorityInField(2,'e') and (self.EMP > 0 or self.extraE > 0):
                    self.capture(self.splitField()[0], self.e) #Capture useful 1* units in field
                elif self.rarityInField(1) and (self.EMP > 0 or self.extraE > 0):
                    self.capture(self.field[-1], self.e) #Capture misc 1* units to thin pool
                
                elif len(self.pool) <= 4 and self.aidCom > 0 and len(self.pool) > 0:
                    self.svarog() #Use Svarog if pool is 4 or smaller. Equal or greater chance for RL than impulse
                elif self.refreshCD == 0:
                    self.refresh()
                    
                elif self.priorityInField(3) and (self.EMP > 0 or self.extraE > 0):
                    self.capture(self.field[0], self.e) #Use impulses to capture useful 2* as they appear
                    
                elif (self.rarityInField(2,'o') and (self.EMP > 0 or self.extraE > 0) 
                      and self.ratPool() > self.rat1): #Only useless 2* remains. Use impulses only if 1* ratio is higher than target
                    self.capture(self.field[0], self.e)
                elif self.aidCom > 0 and len(self.pool) > 0:
                    self.svarog() #Use aid commissions in other scenarios.
                elif self.aidCom == 0 and len(self.pool) > 0:
                    self.whale()
                else: self.timestep()

class SKK(object):
    """An instance of our unfortunate character who will exist only briefly to collect robotic women, then disappear once more"""
    def __init__(self, params: dict, banners: dict):
        self.p = params
        self.b = banners
        self.blen = len(self.b)
        self.prio = self.p["PriorityMin"]
        self.RLprio = self.p["RLPriorityMin"]
        self.impulse = self.p["InitialEMP"]
        self.extraImpulse = self.p["MonthlyExtraImpulse"][0]
        self.aidCom = self.p["MonthlyAidCommisions"][0]
        self.poolReset = self.p["PoolResetOnRLCap"] #Whether to choose to reset the pool upon ringleader capture
        self.dlim = self.p["DesireLimit"] #Global limit on how much a single unit can be prioritised in a single banner
        self.rat1 = self.p["Ratio1"] #The ratio of 1* units to others, to determine choice of svarog
        self.armoury = {} #Units captured using standard means
        self.whalemoury = {} #Units that would be added using whaled aid commission tickets
        self.debt = 0 #160 gems per aid commission, 112 on sale
        self.collect = self.p["CollectAllRL"] #Parameter of whether to collect all ringleaders, or only follow priority list
        self.monthEndRSC = {"Impulse":[], "XImpulse": [], "AidCom":[]} #Random metrics
        self.fcRL = 0 #Count of ringleaders collected for free
        self.rlpsz = {"Impulse":[], "XImpulse": [], "Aid":[], "Whale":[]}
        self.RLAction = [] #List of the number of capture actions used to capture the RL in each banner. 0 for no capture
        self.fWitness = [] #List of the number of RL sightings that SKK had in each banner
        
    def deposit(self, catches: list, overFishing: list):
        """Records the captures of the month into SKK's display case"""
        for i in catches:
            if self.mCap.b[i]["Rarity"] == 3: self.fcRL += 1
            if i in self.armoury.keys(): self.armoury[i] += 1
            else: self.armoury[i] = 1
        # Records the captures of the month that involved money into a different display case
        for j in overFishing:
            self.debt += 1
            if j in self.whalemoury.keys(): self.whalemoury[j] += 1
            else: self.whalemoury[j] = 1
        
    def upkeep(self,emp: int, xmp: int, svr: int, mn: int, mrlpsz: dict, mAction: int, sights: int):
        """
        Updates the impulses and aid commisions available to be used next month
        Records specified monthly statistics
        """
        self.impulse = emp
        self.extraImpulse = xmp
        self.aidCom = svr
        if self.mCap.RL: self.RLAction.append(mAction) #Record number of capture actions before RL capture
        else: self.RLAction.append(0) #0 for no RL capture in banner
        self.fWitness.append(sights) #Number of sightings of RL for free
        
        self.monthEndRSC["Impulse"].append(self.impulse-1)
        self.monthEndRSC["XImpulse"].append(self.extraImpulse)
        self.monthEndRSC["AidCom"].append(self.aidCom)
        
        if mn+1 < len(self.b):
            self.extraImpulse += self.p["MonthlyExtraImpulse"][(mn+1)%len(self.p["MonthlyExtraImpulse"])]
            self.aidCom += self.p["MonthlyAidCommisions"][(mn+1)%len(self.p["MonthlyAidCommisions"])]
        for i in mrlpsz:
            self.rlpsz[i].extend(self.mCap.rlpsz[i])
        
        
    def LTsim(self): #-> tuple:
        """Run banner simulations, passing forward capture related resources to the following cycle"""
        for mn in range(self.blen):
            global glog
            if glog:
                global glof
                glof.write("New month\n\n")
            
            self.mCap = simMonthly(self.p["Duration"], self.impulse, self.extraImpulse, self.aidCom,
                                   self.b[mn], self.prio, self.collect, self.poolReset, self.dlim,
                                   self.RLprio, self.rat1)
            self.mCap.runSim()
            self.deposit(self.mCap.claims, self.mCap.wclaims)
            self.upkeep(self.mCap.EMP, self.mCap.extraE, self.mCap.aidCom, mn, 
                        self.mCap.rlpsz, self.mCap.RLAction, self.mCap.witness)
    
    
class MrPickle(object):
    """
    A dummy class object used to store variables and values, used to replot results without having to rerun the simulatiom
    """
    def __init__(self, nSKK, dt, Armoury, Whaling, endRSC, 
                 Wallet, Banners, RLCount, RLCPoolSz, 
                 CaptureParams, RLActionCount, fSightings):
        self.dt = dt
        self.Armoury = Armoury
        self.Whaling = Whaling
        self.endRSC = endRSC
        self.Wallet = Wallet
        self.Banners = Banners
        self.RLCount = RLCount
        self.RLCPoolSz = RLCPoolSz
        self.nSKK = nSKK
        self.CaptureParams = CaptureParams
        self.RLActionCount = RLActionCount
        self.fSightings = fSightings
        



if __name__ == '__main__':
    t1 = datetime.datetime.now()
    dirfils = os.listdir()
    random.seed(0)
    paramfil = "Params2trunc.json"
    
    global glog
    glog = False
    if glog:
        global glof
        glofile = "PA-LT\\jank.txt"
        glof = open(glofile, "w") #Jank choice of creating a global file object to dump intermediate information
    
    with open(paramfil,'r') as f:
    #Import settings and whatever junk from json file
        settingsIn = json.load(f)
        nSKK = settingsIn["nSKK"]
        CaptureParams = settingsIn["CaptureParams"]
        Banners = settingsIn["Banners"]
        DataDisplay = settingsIn["DataDisplay"]
    print("Now running: {}\n".format(paramfil))
    for se in CaptureParams:
        print("{}: {}".format(se, CaptureParams[se]))
    print('{} simulated players'.format(nSKK))
    print('{} banner periods\n'.format(len(Banners)))
    xLen = list(range(len(Banners)))
    Armoury = {} #Units captured using free methods
    Whaling = {} #Units captured using whale commissions
    Wallet = [] #List of amount of tickets or gems required to compelte all goals
    RLCount = [] #List of number of Ringleaders captured for free
    endRSC = {"Impulse":[0]*len(Banners), "XImpulse": [0]*len(Banners), "AidCom":[0]*len(Banners)}
    RLCPoolSz = {"Impulse":[], "XImpulse":[], "Aid":[], "Whale":[]}
    RLActionCount = [] #Number of pull actions to capture first RL within a single banner
    fSightings = [] #Number of sightings of RL for free within a single banner
        
    for i in range(nSKK):
        if i % 2500 == 0: print("Progressing, trial number {}".format(i))
        if i % 10000 == 0:
            t4 = datetime.datetime.now()
            print("Time elapsed: {} seconds".format((t4-t1).seconds))
        iskk = SKK( params = CaptureParams,banners = Banners)
        iskk.LTsim()
        
        for j in iskk.whalemoury:
            if j in Whaling: Whaling[j].append(iskk.whalemoury[j])
            else: Whaling[j] = [iskk.whalemoury[j]]
        for i in iskk.armoury:
            if i in Armoury: Armoury[i].append(iskk.armoury[i])
            else: Armoury[i] = [iskk.armoury[i]]
            if i not in Whaling: Whaling[i] = []
            
        Wallet.append(iskk.debt)
        RLCount.append(iskk.fcRL)
        RLActionCount += iskk.RLAction
        fSightings += iskk.fWitness
        
        for i in iskk.rlpsz: RLCPoolSz[i].extend(iskk.rlpsz[i])
        for k in endRSC:
            for h in xLen:
                endRSC[k][h] += iskk.monthEndRSC[k][h]
    for k in endRSC: endRSC[k] = [round(j/nSKK,2) for j in endRSC[k]]
    
    if glog: glof.close() #lol
    
    t2 = datetime.datetime.now()
    dt = t2-t1
    
    dtm = int(dt.seconds/60)
    dts = dt.seconds % 60
    fpth = os.path.join("PA-LT","{}k SKK - {}".format(nSKK//1000, str(t2)[:-7].replace(':','')))
    os.mkdir(fpth)
    fpth += "\\"
    Jar = MrPickle(nSKK = nSKK, dt = dt, Armoury = Armoury, 
                   Whaling = Whaling, endRSC = endRSC, Wallet = Wallet, Banners = Banners, 
                   RLCount = RLCount, RLCPoolSz = RLCPoolSz, CaptureParams = CaptureParams,
                   RLActionCount = RLActionCount, fSightings = fSightings)
    with open(fpth + "jar.pickle",'wb') as f1: pickle.dump(Jar, f1)
    
    plt.rc('axes', titlesize=23)
    plt.rc('axes', labelsize=22)
    plt.rc('xtick', labelsize=20)
    plt.rc('ytick', labelsize=20)
    
    px = 1/plt.rcParams['figure.dpi']
    fig, axs = plt.subplots(3,3,figsize=(DataDisplay["ImageSize"]["W"]*px,DataDisplay["ImageSize"]["H"]*px))
    plur = 's'
    if len(Banners) == 1: plur = ''
    fig.suptitle("Extended time SF Capture simulation\n{} banner period{}, {} simulated players\n".format(len(Banners), plur, nSKK), fontsize = 28)

    #Proportion of capture of ringleaders  
    aList, wList, oList, rList, eList = [[],[],[]],[[],[],[]],[],[],[[],[],[]]
    for n in Banners:
        for p in n:
            if n[p]["Rarity"] == 3 and p not in rList: rList.append(p)
            elif n[p]["Rarity"] == 2 and p not in eList[2]: eList[2].append(p)
            elif n[p]["Rarity"] == 1 and p not in eList[1]: eList[1].append(p)
    for m in rList:
        aList[0].append(np.round(sum(Armoury[m])/nSKK,3))
        wList[0].append(np.round(sum(Whaling[m])/nSKK,3))
    for h in eList[1]:
        aList[1].append(np.round(sum(Armoury[h])/nSKK,1))
        wList[1].append(np.round(sum(Whaling[h])/nSKK,1))
    for hr in eList[2]:
        aList[2].append(np.round(sum(Armoury[hr])/nSKK,1))
        wList[2].append(np.round(sum(Whaling[hr])/nSKK,1))
    
    b4 = axs[0,0].bar(rList,aList[0],label = 'Free capture')
    b5 = axs[0,0].bar(rList,wList[0],label = 'Whale capture',bottom = aList[0])
    axs[0,0].legend(fontsize = 13,loc = 4)
    axs[0,0].xaxis.set_major_locator(mticker.FixedLocator(axs[0,0].get_xticks()))
    axs[0,0].set_xticklabels(labels = rList, fontsize = 14, rotation = 50)
    axs[0,0].bar_label(b4, fontsize = 14, label_type = 'center')
    axs[0,0].bar_label(b5, fontsize = 14, label_type = 'center')
    axs[0,0].set_title("Proportion of ringleader captures: F2P and whale")
    axs[0,0].set_xlim(xmin = -0.5, xmax = len(rList)-0.5)
    if not CaptureParams["PoolResetOnRLCap"]: axs[0,0].set_ylim(ymax = 1)
    
    #Volume of capture for 1* units
    b6 = axs[1,1].bar(eList[1],aList[1],label = 'Free capture')
    b7 = axs[1,1].bar(eList[1],wList[1],label = 'Whale capture',bottom = aList[1])
    axs[1,1].legend(fontsize = 14)
    axs[1,1].xaxis.set_major_locator(mticker.FixedLocator(axs[1,1].get_xticks()))
    axs[1,1].set_xticklabels(labels = eList[1], fontsize = 14, rotation = 90)
    axs[1,1].bar_label(b6, fontsize = 14, label_type = 'center')
    axs[1,1].bar_label(b7, fontsize = 14, padding = 4)
    axs[1,1].set_title("Volume of regular 1* unit captures: F2P and whale")
    axs[1,1].set_ylim(ymin = 0, ymax = int(max([sum(x) for x in zip(aList[1],wList[1])])*1.1))
    
    #Volume of capture for 2* units
    b8 = axs[1,2].bar(eList[2],aList[2],label = 'Free capture')
    b9 = axs[1,2].bar(eList[2],wList[2],label = 'Whale capture',bottom = aList[2])
    axs[1,2].legend(fontsize = 14)
    axs[1,2].xaxis.set_major_locator(mticker.FixedLocator(axs[1,2].get_xticks()))
    axs[1,2].set_xticklabels(labels = eList[2], fontsize = 14, rotation = 90)
    axs[1,2].bar_label(b8, fontsize = 14, label_type = 'center')
    axs[1,2].bar_label(b9, fontsize = 14, padding = 4)
    axs[1,2].set_title("Volume of regular 2* unit captures: F2P and whale")
    axs[1,2].set_ylim(ymin = 0, ymax = int(max([sum(x) for x in zip(aList[2],wList[2])])*1.1))
    
    #Remaining resources
    barW = DataDisplay["GroupBarWidth"]
    xb = np.arange(len(xLen)+1)[1:]
    b1 = axs[0,1].bar(xb-barW,endRSC["Impulse"], width = barW, label = "Impulse")
    b2 = axs[0,1].bar(xb,endRSC["XImpulse"], width = barW, label = "Extra impulses")
    b3 = axs[0,1].bar(xb+barW,endRSC["AidCom"], width = barW, label = "Aid commissions")
    axs[0,1].set_xticks(xb)
    axs[0,1].set_title("Remaining resources on month end")
    axs[0,1].legend(loc = 2,fontsize = 14)
    
    axs[0,1].bar_label(b1, padding = 5,fontsize=12, rotation = 90)
    axs[0,1].bar_label(b2, padding = -5,fontsize=12, rotation = 90)
    axs[0,1].bar_label(b3, fontsize=12, rotation = 90, label_type = 'center')
    axs[0,1].set_xlim(xmin = 0.5, xmax = len(xb)+0.5)
    axs[0,1].set_xlabel("Month number")
    
    #Whaling histogram
    wbins = DataDisplay["WhaleBins"]
    wUnit = 'tickets'
    if DataDisplay['TicketsToGems']:
        wbins = int(wbins*160)
        Wallet = [i*160 for i in Wallet]
        wUnit = 'gems'
    binlim = int(np.ceil(max(Wallet)/wbins))*wbins
    binlist = [0] + list(range(1,binlim+2,wbins))
    binlabels = ['0']
    for j in range(2,len(binlist)):
        binlabels.append(str("{} - {}".format(binlist[j-1],binlist[j]-1)))
    h3, _ = np.histogram(Wallet, bins = binlist)

    if DataDisplay["WhalePercent"]: 
        axs[1,0].yaxis.set_major_formatter(mticker.PercentFormatter(xmax = nSKK, decimals = 1))
    whbars = axs[1,0].bar(binlabels, h3, color = 'dodgerblue')
    axs[1,0].set_title("Total {} expense to complete goals over all periods".format(wUnit[:-1]))
    axs[1,0].tick_params(axis='both', which='major', labelsize=18)
    axs[1,0].set_ylabel("Count SKK")
    axs[1,0].set_xlabel("SKK debt, bin size {} {}".format(wbins,wUnit))
    axs[1,0].set_ylim(ymin = 0, ymax = int(max(h3)*1.13))
    axs[1,0].xaxis.set_major_locator(mticker.FixedLocator(axs[1,0].get_xticks()))
    axs[1,0].set_xticklabels(labels = binlabels, fontsize = 14, rotation = 90)
    axs[1,0].set_xlim(xmin = -0.5, xmax = len(binlist)-1.5)
    axs[1,0].bar_label(whbars, fontsize = 12, label_type = 'edge', padding = 6, rotation = 90)
    
    #Distribution of number of ringleaders captured for free
    rbins = list(range(max(RLCount)+2))
    RLhist, _ = np.histogram(RLCount, rbins)
    if DataDisplay["RLFreePercent"]: 
        axs[2,0].yaxis.set_major_formatter(mticker.PercentFormatter(xmax = nSKK, decimals = 0))
    rlhb = axs[2,0].bar(rbins[:-1], RLhist, color = 'seagreen')
    axs[2,0].set_title("Ringleaders captured F2P")
    axs[2,0].set_xlabel("Number of ringleaders")
    axs[2,0].set_ylabel("Count SKK")
    axs[2,0].set_xlim(xmin=-0.5, xmax = rbins[-2] + 0.5)
    axs[2,0].set_ylim(ymax = max(RLhist)*1.13, ymin = 0)
    axs[2,0].bar_label(rlhb, fontsize = 13, label_type = 'edge', padding = 4, rotation = 90)
    
    #Distribution of pool sizes when ringleader is captured
    RLCPSWhale = DataDisplay["RLCPSWhale"]
    nRLC = len(RLCPoolSz['Impulse']) + len(RLCPoolSz['Aid'])
    if RLCPSWhale: nRLC += len(RLCPoolSz['Whale'])
    pcbins = list(range(102))
    rlpsh, rlpb = [[],[],[],[]], [[],[],[],[]]
    
    rlpsh[0], _ = np.histogram(RLCPoolSz['Impulse'], pcbins)
    rlpsh[1], _ = np.histogram(RLCPoolSz['Aid'], pcbins)
    rlpsh[2], _ = np.histogram(RLCPoolSz['XImpulse'], pcbins)
    
    rlpb[0] = axs[2,1].bar(pcbins[:-1], rlpsh[0], label = "Impulses")
    rlpb[2] = axs[2,1].bar(pcbins[:-1], rlpsh[2], bottom = rlpsh[0] , label = "Extra Impulse")
    rlpb[1] = axs[2,1].bar(pcbins[:-1], rlpsh[1], bottom = rlpsh[0] + rlpsh[2], label = "Free aid")
    if RLCPSWhale:
        rlpsh[3], _ = np.histogram(RLCPoolSz['Whale'], pcbins)
        rlpb[3] = axs[2,1].bar(pcbins[:-1], rlpsh[3], bottom = [rlpsh[2][i] + rlpsh[1][i] + rlpsh[0][i] for i in range(len(rlpsh[0]))], label = "Whale aid")
    if DataDisplay["RLCPSPercent"]: 
        axs[2,1].yaxis.set_major_formatter(mticker.PercentFormatter(xmax = nRLC, decimals = 2))
    axs[2,1].set_title("Pool size during ringleader capture")
    axs[2,1].set_xlabel("Pool size")
    axs[2,1].legend(loc = 'upper right', fontsize = 14)
    axs[2,1].set_ylabel("Count captures")
    axs[2,1].set_xlim(xmin=-0.5, xmax = 100.5)
    
    #Count of pull actions to reach first RL capture
    rbins2 = list(range(max(RLActionCount)+2))
    RLAcHist, _ = np.histogram(RLActionCount, rbins2)
    axs[2,2].yaxis.set_major_formatter(mticker.PercentFormatter(xmax = len(RLActionCount), decimals = 2))
    rlachb = axs[2,2].bar(rbins2[:-1], RLAcHist, color = 'coral')
    axs[2,2].set_title("Actions to first ringleader capture")
    axs[2,2].set_xlabel("Number of actions")
    axs[2,2].set_ylabel("Banner period proportion")
    axs[2,2].set_xlim(xmin=0.5, xmax = rbins2[-2] + 0.5)
    axs[2,2].set_ylim(ymax = max(RLAcHist[1:])*1.08, ymin = 0)
    #axs[2,2].bar_label(rlachb, fontsize = 13, label_type = 'edge', padding = 4, rotation = 90)
    plt.text(0.03,0.98,'{}% of banner periods did not have RL capture'.format(round(RLAcHist[0]/len(RLActionCount)*100,2)),horizontalalignment='left',
             verticalalignment='top', fontsize = 16,  transform = axs[2,2].transAxes)
    
    #Count of sightings of Ringleader for free
    rbins3 = list(range(max(fSightings)+2))
    fSHist, _ = np.histogram(fSightings, rbins3)
    axs[0,2].yaxis.set_major_formatter(mticker.PercentFormatter(xmax = len(fSightings), decimals = 2))
    fshb = axs[0,2].bar(rbins3[:-1], fSHist, color = 'crimson')
    axs[0,2].set_title("Sightings of ringleader (F2P)")
    axs[0,2].set_xlabel("Number of sightings")
    axs[0,2].set_ylabel("Banner period proportion")
    axs[0,2].set_xlim(xmin=-0.5, xmax = rbins3[-2] + 0.5)
    axs[0,2].set_ylim(ymax = max(fSHist)*1.04, ymin = 0)
    axs[0,2].bar_label(fshb, fontsize = 10, label_type = 'edge', padding = 1, rotation = 90)
    
    #Whatever the heck this does, but it makes the exported image not look as stupid
    fig.tight_layout()
   
    
    plt.text(-0.08,1.12,'Runtime: {}m{}s'.format(dtm,dts),horizontalalignment='left',
             verticalalignment='bottom', fontsize = 16,  transform = axs[0,0].transAxes)
    plt.text(0.95,1.12,'1* Ratio maximum to Aid: {}'.format(CaptureParams["Ratio1"]),horizontalalignment='right',
             verticalalignment='bottom', fontsize = 16,  transform = axs[0,2].transAxes)
    plt.text(0,1.06,'{}'.format(CaptureParams["Notes"]),horizontalalignment='left',
             verticalalignment='bottom', fontsize = 18,  transform = axs[0,0].transAxes)
    print("Time elapsed: {}m{}s".format(dtm,dts))
    
    fig.savefig(fpth + 'Figure {}.png'.format(str(t2)[:-7].replace(':','')))
    with open(fpth + 'Figure {}.txt'.format(str(t2)[:-7].replace(':','')),'w') as fp:
        for i in CaptureParams:
            fp.write("{}: {}\n".format(i,CaptureParams[i]))
        fp.write('\nRuntime: {}m{}s'.format(dtm,dts))
        fp.write("\n{} players ({}%) completed all goals for free\n".format(Wallet.count(0), round(Wallet.count(0)*100/nSKK,3)))
        fp.write("The most unlucky player was required to spend {} {} to accomplish all goals\n".format(max(Wallet),wUnit))
        fp.write("Average {} expense: {}\n".format(wUnit[:-1],round(np.mean(Wallet))))
        fp.write("Median {} expense: {}\n".format(wUnit[:-1],round(np.median(Wallet))))
    