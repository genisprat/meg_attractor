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
#path='/home/gprat/cluster_archive/Master_Project/preprocess_data'

i=0
# read all epochs and concatanete

Nsigmas=3

#filenames=['/home/gprat/cluster_archive/Master_Project/preprocess_data/resp_sub4_s7_block2-epo.fif.gz','/home/gprat/cluster_archive/Master_Project/preprocess_data/resp_sub4_s7_block3-epo.fif.gz']
filenames=['/mnt/genis/Master_Project/process_data/resp_sub7_s5_block7-epo.fif.gz','/mnt/genis/Master_Project/process_data/resp_sub7_s5_block1-epo.fif.gz']
subjects=[6,10,11,12,15,16,17,18]
subjects=[7]

for subject in subjects:
    meta_all=[[],[],[]]
    rlspock_all=[[],[],[]]

    for filename in glob.glob(os.path.join(path, 'resp_sub'+str(subject)+'_*.fif.gz')):
#        print filename
#    for filename in filenames:
#        filename='/home/gprat/cluster_archive/Master_Project/preprocess_data/resp_sub4_s7_block2-epo.fif.gz'
        sesion=filename[filename.find('_s',48)+2]
        block=filename[filename.find('_block')+6]
        print 'hi'
        filename_meta=path+'/resp_meta_sub'+str(subject)+'_s'+sesion+'_block'+block+'.hdf'
        rlspock=mne.read_epochs(filename)
        meta=pd.read_hdf(filename_meta,'meta')
        meta2=meta
        meta2.index=range(len(meta2))
        meta_aux=meta
        print len(meta2),len(rlspock),sesion,block
        for isigma in range(Nsigmas):     
            meta_all[isigma].append(meta_aux[meta.noise==isigma])
            rlspock_all[isigma].append(rlspock[meta_aux[meta.noise==isigma].index])
        
        
        
        print 'hi2'
    #    
    #    
    #    rlspock_all=rlspock
    #    meta_all=meta
    #    rlspock.info=rlspock_all.info
    #
    print 'data loaded'
    
    meg_data=[]
    meta_data=[]
    decoding=[]
    decoding_err=[]
    for isigma in range(Nsigmas):   
        for i in range(len(rlspock_all[isigma])):
            rlspock_all[isigma][i].info=rlspock_all[isigma][0].info
    
        meg_data.append(mne.epochs.concatenate_epochs(rlspock_all[isigma]))
        meta_data.append(pd.concat(meta_all[isigma]))
        
        gat = meg.decoding.generalization_matrix(meg_data[isigma], meta_data[isigma].response.values, 100)
        g = gat.groupby(["train_time", "predict_time"]).mean()
        
        decoding.append(pd.pivot_table(data=g.reset_index(), values="accuracy", index="train_time", columns="predict_time"))
        h = gat.groupby(["train_time", "predict_time"]).std()
        decoding_err.append(pd.pivot_table(data=h.reset_index(), values="accuracy", index="train_time", columns="predict_time"))
        
        path2='/mnt/genis/Master_Project/results'
        f=open(path2+'/subject_'+str(subject)+'_matrix_sigmas.pickle','w')
        data={}
        data['decoding']=decoding
        data['decding_err']=decoding_err    
        pickle.dump(data,f)
        f.close()