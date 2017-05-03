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
import numpy as np
import matplotlib.colors as colors
#from matplotlib import style
import numpy as np
import matplotlib.cm as cmx	

#subjects=['1''4','5','6','7','8','9','10','11','12','14','15','16','17','18','19']
#subjects=['4','5','6','7','8','9','10','11','12','15','16','18','19']
#subject=int(subjects[int(sys.argv[1])])
subjects=[1,4,5,6,7,8,9,10,11,12,14,15,16,17,18,19]
#path='/mnt/homes/home024/gortega/meg_analysis/preprocess_data'
#path='/mnt/genis/Master_Project/process_data'
#path='/home/genis/cluster_archive/Master_Project/results'
path='/home/gprat/cluster_archive/Master_Project/results'

i=0
# read all epochs and concatanete

Nsigmas=3


cm = plt.get_cmap('hot') 
cNorm  = colors.Normalize(vmin=0, vmax=4)
scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
#obro un per veure com es de llarg el vector
isub=0
path2='/home/genis/cluster_archive/Master_Project/results'
path2=path
f=open(path2+'/subject_'+str(subjects[isub])+'_matrix_sigmas.pickle','rb')
data=pickle.load(f)
decoding=data['decoding']
decoding_err=data['decding_err']    
f.close()
y=np.array(decoding[0])[25,:]
mean_y=np.zeros((3,len(y)))
col=3
row=6

fig=plt.figure()
for isub in range(len(subjects)):
    fig_kernel=fig.add_subplot(row,col,isub+1)
    fig_kernel.text(-2,0.7,'sub '+str(subjects[isub]))
    f=open(path+'/subject_'+str(subjects[isub])+'_matrix_sigmas.pickle','rb')
    data=pickle.load(f)
    decoding=data['decoding']
    decoding_err=data['decding_err']    
    f.close()
    
    for isigma in range(Nsigmas):
        y=np.array(decoding[isigma])[25,:]
        y_err=np.array(decoding_err[isigma])[25,:]
        mean_y[isigma]=mean_y[isigma]+y
#        y=np.diagonal(decoding[isigma])
#        y_err=np.diagonal(decoding_err[isigma])
        
        x=np.linspace(-2.5,0.5,len(y))
    
#        plt.errorbar(x,y,y_err,color=scalarMap.to_rgba(isigma))
        plt.plot(x,y,color=scalarMap.to_rgba(isigma))
        plt.plot(x,np.zeros(len(x)),'g--')
        plt.ylim(0.40,0.8)

fig_kernel=fig.add_subplot(row,col,row*col)
for isigma in range(Nsigmas):
    plt.plot(x,mean_y[isigma]/len(subjects),color=scalarMap.to_rgba(isigma))