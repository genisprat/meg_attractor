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
subject=10
#path='/mnt/homes/home024/gortega/meg_analysis/preprocess_data'
#path='/mnt/genis/Master_Project/'
path='/home/genis/cluster_archive/Master_Project/preprocess_data'
i=0
# read all epochs and concatanete
rlspock_all=[]
meta_all=[]
for filename in glob.glob(os.path.join(path, 'resp_sub'+str(subject)+'_*.fif.gz')):
#    print filename
#for i in range(1):
    filename='/home/genis/cluster_archive/Master_Project/preprocess_data/resp_sub4_s7_block2-epo.fif.gz'
    sesion=filename[filename.find('_s',65)+2]
    block=filename[filename.find('_block',65)+6]
    print 'hi'
    filename_meta=path+'/resp_meta_sub'+str(subject)+'_s'+sesion+'_block'+block+'.hdf'
    rlspock=mne.read_epochs(filename)
    meta=pd.read_hdf(filename_meta,'meta')
    print 'hi2'
#    
#    
    rlspock_all=rlspock
    meta_all=meta
    rlspock.info=rlspock_all.info

rlspock_all=mne.epochs.concatenate_epochs([rlspock_all,rlspock])
meta_all=pd.concat([meta_all,meta])
    
print 'data loaded'
gat = meg.decoding.generalization_matrix(rlspock_all, meta_all.response.values, 100)
g = gat.groupby(["train_time", "predict_time"]).mean()
o = pd.pivot_table(data=g.reset_index(), values="accuracy", rows="train_time", cols="predict_time")

path2='/mnt/genis/Master_Project/meg_analysis/decoding_data/'
f=open(path2+'subject_'+str(subject)+'_matrix.pickle','w')
pickle.dump(o,f)
f.close()