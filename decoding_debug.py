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
subject=6
#path='/mnt/homes/home024/gortega/meg_analysis/preprocess_data'
path='/mnt/genis/Master_Project/process_data'
#path='/home/genis/cluster_archive/Master_Project/preprocess_data'
i=0
# read all epochs and concatanete
rlspock_all=[]
meta_all=[]
#filenames=['/mnt/genis/Master_Project/process_data/resp_sub7_s7_block1-epo.fif.gz','/mnt/genis/Master_Project/process_data/resp_sub7_s5_block1-epo.fif.gz']
meta_all=[]
rlspock_all=[]
Nsigmas=3

channels_out={}
channels_out['subject']=[]
channels_out['session']=[]
channels_out['block']=[]
channels_out['channels']=[]
f=open('/mnt/genis/Master_Project/process_data/all_channels.pickle','rb')
all_channels=pickle.load(f)
f.close()

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
#    for itrial in range(len(meta)):
#        meta_all[meta.iloc[itrial].noise].append(meta.iloc[itrial])
#        rlspock_all[meta.iloc[itrial].noise].append(rlspock[itrial])
        
    print 'hi2'
#    
#    
    rlspock_all.append(rlspock)
    meta_all.append(meta)
#    all info equal to concatanate
#for i in range(len(rlspock_all)):
#    for j in range()
nchan=[]
sesions=[]
blocks=[]

for iblock in range(len(rlspock_all)):
#    for itrial in range(len(rlspock_all[iblock])):
    rlspock_all[iblock].info['dev_head_t']=rlspock_all[0].info['dev_head_t']
    nchan.append(rlspock_all[iblock].info['nchan'])
    sesions.append(sesions)
    blocks.append(block)
    ch_out=[]
    if rlspock_all[iblock].info['nchan'] <len(all_channels):
        for ich in range(len(all_channels)):
            if all_channels[ich] not in  rlspock_all[iblock].info['ch_names']:
                ch_out.append(rlspock_all[iblock].info['ch_names'][ich])
        channels_out['subject'].append(subject)
        channels_out['session'].append(sesion)
        channels_out['block'].append(block)
        channels_out['channels'].append(ch_out)

f=open(path+'/channels_out_sub'+str(subject)+'.pickle','wb')
pickle.dump(channels_out,f)
f.close()

    
#    for itrial in range(len(rlspock_all[iblock])):
#        nchan.append(rlspock_all[iblock][itrial].info['nchan'])
#rlspock_all=mne.epochs.concatenate_epochs(rlspock_all)
#meta_all=pd.concat(meta_all)
    
#print 'data loaded'
#gat = meg.decoding.generalization_matrix(rlspock_all, meta_all.response.values, 100)
#g = gat.groupby(["train_time", "predict_time"]).mean()
#o = pd.pivot_table(data=g.reset_index(), values="accuracy", rows="train_time", cols="predict_time")
#
#path2='/mnt/genis/Master_Project/meg_analysis/decoding_data/'
#f=open(path2+'subject_'+str(subject)+'_matrix.pickle','w')
#pickle.dump(o,f)
#f.close()