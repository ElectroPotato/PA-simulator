# -*- coding: utf-8 -*-
"""
Created on Wed 30 Jun 2021

@author: Potato
"""
import random
import datetime

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
        
    def timestep(self):
        self.t += 0.5
        if self.refreshCD > 0: self.refreshCD -= 0.5
        if self.EMP < 14: self.EMP += 1
        
    def refresh(self):
        self.field = random.sample(self.pool,3)
        self.refreshCD = 3
    
    def svarog(self):
        self.aidCom -= 1
        a = random.choice(self.pool)
        self.pool.remove(a)
        self.claims.append(a)
        self.maintain()
        if a == '3*': self.cday=self.t
        assert self.aidCom >= 0
        
    def capture(self, doll, e = 'e'):
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

if __name__ == '__main__':
    t1 = datetime.datetime.now()
    
    a = 28 #Number of days to simulate (Default: 28)
    b = 0 #Number of normal EMPs to start with
    c = 5 #Number of surplus EMPs to use in simulation
    d = 4 #Number of Svarog aid commision tickets to use in simulation
    e = 3 #Days of cooldown before field refresh is available at start of simulation (Default: 3)
    nTrials = 100000
    
    counts = {"Seen": 0, "Captured": 0, "Sightings": [], "Capture day": []}
    for i in range(nTrials):
        trial = simBanner(a,b,c,d,e)
        while trial.t <= trial.days:
            if trial.t != trial.days:
                if trial.EMP == 0: 
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
                elif '1*' in trial.field and trial.extraE > 0:
                    trial.capture('1*','x')
                elif '2*' in trial.field and trial.extraE > 0:
                    trial.capture('2*','x')
                elif trial.aidCom > 0:
                    trial.svarog()
                else: trial.timestep()
        if '3*' in trial.claims: counts['Captured'] += 1
        if trial.witness > 0: counts['Seen'] += 1
        counts['Sightings'].append(trial.witness)
        if trial.cday != -1: counts["Capture day"].append(int(trial.cday))
    print("Capture rate: {}/{} ({}%)\nSeen: {}/{} ({}%)".format(counts["Captured"],nTrials,
                                                                round(counts["Captured"]/nTrials*100,2),
                                                                counts["Seen"],nTrials,
                                                                round(counts["Seen"]/nTrials*100,2)))
    f = counts["Capture day"].count(a)
    print("Proportion of captures occurring on the final day: {}%\n".format(round(f/nTrials*100,2)))
    t2 = datetime.datetime.now()
    print("Time elapsed: {} seconds".format((t2-t1).seconds))
    
'''    
    import matplotlib.pyplot as plt
    q = list(range(max(counts['Sightings'])+1))
    p = list(range(a+1))
    plt.figure()
    plt.hist(counts['Sightings'], bins = q)
    plt.title('Sightings')
    plt.figure()
    plt.hist(counts['Capture day'], bins = p)
    plt.title('Capture day')
'''              
            
    
    
