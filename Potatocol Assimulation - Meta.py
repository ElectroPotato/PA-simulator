# -*- coding: utf-8 -*-
"""
Created on Wed 30 Jun 2021

@author: Potato
"""
import random
import datetime
import numpy as np

import pickle
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

class simBanner(object):
    
    def __init__(self,days,initEMP, extraE, aidCom, refreshCD = 3):
        self.days, self.EMP, self.extraE, self.aidCom, self.refreshCD = days, initEMP, extraE, aidCom, refreshCD
        self.pool = ['3*']+['2*']*21+['1*']*78
        self.t = 0
        self.field = random.sample(self.pool,3)
        self.claims = []
        self.dolltypes = ['3*','2*','1*']
        self.e = 'e'
        self.witness = 0
        self.cday = -1
        self.refreshCall = []
        self.countE = 0
        self.countA = 0
        self.capE = 0
        self.capA = 0
        
    def timestep(self):
        self.t += 0.5
        if self.refreshCD > 0: self.refreshCD -= 0.5
        if self.EMP < 14 and self.t < self.days: self.EMP += 1
        
    def refresh(self):
        self.field = random.sample(self.pool,3)
        self.refreshCD = 3
        self.refreshCall.append(int(self.t))
    
    def svarog(self):
        self.aidCom -= 1
        self.countA += 1
        a = random.choice(self.pool)
        self.pool.remove(a)
        self.claims.append(a)
        self.maintain()
        if a == '3*': 
            self.cday=self.t
            self.capA = self.countA
            self.witness += 1
        
        assert self.aidCom >= 0
        
    def capture(self, doll, e = 'e'):
        self.countE += 1
        if e == 'x':self.extraE -= 1
        else: self.EMP -= 1
        if doll == '1*':
            self.pool.remove(doll)
            self.claims.append(doll)
        if doll == '2*':
            c = random.choice([1,0])
            if c == 1:
                self.pool.remove(doll)
                self.claims.append(doll)
        if doll == '3*':
            self.witness += 1
            c = random.choice([1,0,0,0])
            if c == 1:
                self.pool.remove(doll)
                self.claims.append(doll)
                self.cday = self.t
                self.capE = self.countE
        self.field.remove(doll)
        q = self.pool.copy()
        q.remove(self.field[0])
        q.remove(self.field[1])
        self.field.append(random.choice(q))
        del q
        assert self.EMP >= 0
        assert self.extraE >= 0
    
    def maintain(self):
        for i in self.field.copy():
            if self.field.count(i) > self.pool.count(i):
                self.field.remove(i)
                q = self.pool.copy()
                q.remove(self.field[0])
                q.remove(self.field[1])
                self.field.append(random.choice(q))
                del q

def simNTrials(nTrials,a,b,c,d,e = 3):
    co = {"S": 0, "C": 0, "E":0, "A":0}
    for i in range(nTrials):
        if i % 50000 == 0: print("Progressing, trial {}-{} number {}".format(c,d,i))
        trial = simBanner(a,b,c,d,e)
        while trial.t <= trial.days:
            if trial.t != trial.days:
                if trial.EMP == 0 and trial.refreshCD == 0 and '3*' not in trial.field and '1*' not in trial.field:
                    trial.refresh()
                elif trial.EMP == 0: 
                    trial.timestep()
                elif '3*' in trial.field:
                    trial.capture('3*')
                elif '1*' in trial.field:
                    trial.capture('1*')
                elif trial.refreshCD == 0:
                    trial.refresh()
                elif trial.EMP < 14:
                    trial.timestep()
                elif trial.EMP == 14:
                    trial.capture('2*')
            elif trial.t == trial.days:
                if trial.EMP == 0: trial.e = 'x'
                if '3*' in trial.field and (trial.EMP > 0 or trial.extraE > 0):
                    trial.capture('3*',trial.e)
                if len(trial.pool) <= 4:
                    trial.svarog()
                elif '1*' in trial.field and trial.EMP > 0:
                    trial.capture('1*')
                elif trial.refreshCD == 0:
                    trial.refresh()
                elif '2*' in trial.field and trial.EMP > 0:
                    trial.capture('2*')
                elif '1*' in trial.field and trial.extraE > 0:
                    trial.capture('1*','x')
                elif '2*' in trial.field and trial.extraE > 0:
                    trial.capture('2*','x')
                elif trial.aidCom > 0:
                    trial.svarog()
                else: trial.timestep()
        if '3*' in trial.claims: 
            co['C'] += 1
            co['E'] += trial.capE
            co['A'] += trial.capA
        if trial.witness > 0: co['S'] += 1
    C = round(co["C"]/nTrials*100,2)
    S = round(co["S"]/nTrials*100,2)
    E = co['E']/co['C']
    A = co['A']/co['C']
    return S, C, E, A
    
if __name__ == '__main__':
    t1 = datetime.datetime.now()
    
    a = 28 #Number of days to simulate (Default: 28)
    b = 4 #Number of normal EMPs to start with
    c = 13 #Range of surplus EMPs to use in simulation
    d = 7 #Range of Svarog aid commision tickets to use in simulation
    e = 3 #Days of cooldown before field refresh is available at start of simulation (Default: 3)
    nTrials = 200000
    
    countS = np.zeros([d,c])
    countC = np.zeros([d,c])
    countA = np.zeros([d,c])
    countE = np.zeros([d,c])
    
    dirfils = os.listdir()
    if 'PA-countC.pickle' in dirfils:
        with open('PA-countS.pickle','rb') as f1:
            countS = pickle.load(f1)
        with open('PA-countC.pickle','rb') as f2:
            countC = pickle.load(f2)
        with open('PA-countE.pickle','rb') as f3:
            countE = pickle.load(f3)
        with open('PA-countA.pickle','rb') as f4:
            countA = pickle.load(f4)
    
    else:
        for i in range(c):
            for j in range(d):
                countS[j,i], countC[j,i], countE[j,i], countA[j,i] = simNTrials(nTrials,a,b,i,j,e)
                t4 = datetime.datetime.now()
                print("Time elapsed: {} seconds".format((t4-t1).seconds))
            

        with open('PA-countS.pickle','wb') as f1:
            pickle.dump(countS,f1)
        with open('PA-countC.pickle','wb') as f2:
            pickle.dump(countC,f2)
        with open('PA-countE.pickle','wb') as f3:
            pickle.dump(countE,f3)
        with open('PA-countA.pickle','wb') as f4:
            pickle.dump(countA,f4)

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



    
    
