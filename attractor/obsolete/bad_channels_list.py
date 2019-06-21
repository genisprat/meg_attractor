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
import time
    



subjects=['1','4','5','6','7','8','9','10','11','12','14','15','16','17','18','19']
#subjects=['4','5','6','7','8','9','10','11','12','15','16','18','19']
#subject=int(subjects[int(sys.argv[1])])
#subject=11
#path0='/mnt/homes/home024/gortega/meg_analysis'
path0='/mnt/genis/Master_Project'
#path0='/home/genis/cluster_archive/Master_Project'

path=path0+'/process_data'

#path='/home/gprat/cluster_archive/Master_Project/preprocess_data'

path2=path0+'/results'
i=0
# read all epochs and concatanete

Nsigmas=3

#filenames=['/home/gprat/cluster_archive/Master_Project/preprocess_data/resp_sub4_s7_block2-epo.fif.gz','/home/gprat/cluster_archive/Master_Project/preprocess_data/resp_sub4_s7_block3-epo.fif.gz']
#filenames=['/mnt/genis/Master_Project/process_data/resp_sub7_s5_block7-epo.fif.gz','/mnt/genis/Master_Project/process_data/resp_sub7_s5_block1-epo.fif.gz']
#subjects=[6,10,11,12,15,16,17,18]
#subjects=[17]
#subject=subjects[int(sys.argv[1])]
t_i=time.time()

for subject in subjects:
    print 'subject: ',subject
    for filename in glob.glob(os.path.join(path, '*bstat_sub'+str(subject)+'_*')):
#        print filename
    #    for filename in filenames:
    #        filename='/home/gprat/cluster_archive/Master_Project/preprocess_data/resp_sub4_s7_block2-epo.fif.gz'
    #        filename='/mnt/genis/Master_Project/process_data/resp_sub7_s5_block3-epo.fif.gz'
        if len(str(subject))==2:
            aux_pos=4
        else:
            aux_pos=3
        sesion=filename[filename.find(str(subject)+'_s',30)+aux_pos]
        
        block=filename[filename.find('_block')+6]
        f=open(filename,'r')
#        block_stat=pickle.loads(filename)
        block_stat=pickle.load(f)
        f.close()
        try :
            if len(block_stat['bad_channels'])>0:
                print sesion,block,block_stat['bad_channels']
        except KeyError:
            print 'no_data',sesion,block


print 'all_done',(time.time()-t_i)/60.0        
