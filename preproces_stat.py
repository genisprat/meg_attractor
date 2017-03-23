#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 12:23:11 2016
preprocess_stat.
@author: crm
"""
import meg
import mne
import pickle
import sys
import glob
import os
import numpy as np
import pandas as pd
path='/mnt/homes/home024/gortega/meg_analysis/preprocess_data/'
block_stat={}
block_stat['num_blinks']=[]
block_stat['num_cars']=[]
block_stat['num_muscle']=[]
block_stat['num_jumps']=[]
block_stat['total_trials']=[]
block_stat['valid_trials']=[]
block_stat['subject']=[]

subjects=['1','4','5','6','7','8','9','10','11','12','14','15','16','17','18','19']
    
total_vtrials=0
total_trials=0
for isub in range(len(subjects)):
    
    block_stat['num_blinks'].append(0)
    block_stat['num_cars'].append(0)
    block_stat['num_muscle'].append(0)
    block_stat['num_jumps'].append(0)
    block_stat['total_trials'].append(0)
    block_stat['valid_trials'].append(0)
    for filename in glob.glob(os.path.join(path, '*bstat*sub'+subjects[isub]+'_*.pickle')):
        if isub==4:
            print filename
        try:
            f=open(filename,'r')
            data=pickle.load(f)
            f.close()
            bnum=data['bnum']
            snum=int(data['session']-5)
            block_stat['valid_trials'][isub]+=total_vtrials+data['num_valid_trials']
            block_stat['total_trials'][isub]+=data['num_trials']
            block_stat['num_blinks'][isub]=data['num_blinks']
            block_stat['num_cars'][isub]=data['num_cars']
            block_stat['num_muscle'][isub]=data['num_muscle']
            block_stat['num_jumps'][isub]=data['num_jumps']
            if isub==4:
                print data['num_valid_trials'],data['num_trials']
        except EOFError:
            
            print 'Can not open',f



    block_stat['subject'].append(int(subjects[isub]))
#    block_stat['num_blinks']=len(artdef['blinks'].onset)
#    block_stat['num_cars']=len(artdef['cars'])
#    block_stat['num_muscle']=len(artdef['muscle'])
#    block_stat['num_jumps']=len(artdef['jumps'])
#    block_stat['trial_repeat']=trial_repeat
#    block_stat['subject']=subject
#    block_stat['bnum']=bnum
    
bstat=pd.DataFrame(block_stat)
bstat.to_csv(path+'summary_stat.csv')
print block_stat

