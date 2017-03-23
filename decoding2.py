#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 16 14:20:03 2016

@author: crm
script to decode decision variable
"""

import pymeg as meg
import mne
import glob
import os
import pandas as pd
import pylab as plt
import pickle
import sys



subjects=['1''4','5','6','7','8','9','10','11','12','14','15','16','17','18','19']
#subjects=['4','5','6','7','8','9','10','11','12','15','16','18','19']
#subject=int(subjects[int(sys.argv[1])])
subject=7
#path='/mnt/homes/home024/gortega/meg_analysis/preprocess_data'
path='/mnt/genis/Master_Project/process_data/'
#path='/home/genis/cluster_archive/Master_Project/preprocess_data'
i=0
# read all epochs and concatanete
rlspock_all=[]
meta_all=[]
filenames=['/mnt/genis/Master_Project/process_data/resp_sub7_s5_block7-epo.fif.gz','/mnt/genis/Master_Project/process_data/resp_sub7_s5_block1-epo.fif.gz']
meta_all=[[],[],[]]
rlspock_all=[[],[],[]]
Nsigmas=3
for filename in glob.glob(os.path.join(path, 'resp_sub'+str(subject)+'_*.fif.gz')):
#    print filename
#for filename in filenames:
#    filename='/home/genis/cluster_archive/Master_Project/preprocess_data/resp_sub4_s7_block2-epo.fif.gz'
    sesion=filename[filename.find('_s',48)+2]
    block=filename[filename.find('_block')+6]
    print 'hi'
    filename_meta=path+'/resp_meta_sub'+str(subject)+'_s'+sesion+'_block'+block+'.hdf'
    rlspock=mne.read_epochs(filename)
    meta=pd.read_hdf(filename_meta,'meta')
    for itrial in range(len(meta)):
        meta_all[meta.iloc[itrial].noise].append(meta.iloc[itrial])
        rlspock_all[meta.iloc[itrial].noise].append(rlspock[itrial])
        
    print 'hi2'
#    
#    
#    rlspock_all.append(rlspock)
#    meta_all.append(meta)
#    all info equal to concatanate
for isigma in range(len(rlspock_all)):
    for itrial in range(len(rlspock_all[isigma])):
        rlspock_all[isigma][itrial].info['dev_head_t']=rlspock_all[isigma][0].info['dev_head_t']

    rlspock_all[isigma]=mne.epochs.concatenate_epochs(rlspock_all[isigma])
    meta_all[isigma]=pd.concat(meta_all[isigma])
    
#print 'data loaded'
#gat = meg.decoding.generalization_matrix(rlspock_all, meta_all.response.values, 100)
#g = gat.groupby(["train_time", "predict_time"]).mean()
#o = pd.pivot_table(data=g.reset_index(), values="accuracy", rows="train_time", cols="predict_time")
#
#path2='/mnt/genis/Master_Project/meg_analysis/decoding_data/'
#f=open(path2+'subject_'+str(subject)+'_matrix.pickle','w')
#pickle.dump(o,f)
#f.close()