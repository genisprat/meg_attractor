#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 09:52:50 2017

@author: gprat
"""

import pylab as plt
import pickle
import pandas as pd
import numpy as np
import matplotlib.colors as colors
from matplotlib import style
import numpy as np
import matplotlib.cm as cmx
from mpl_toolkits.axes_grid.inset_locator import inset_axes

#subjects=[6,8,10,11,12,15,16,17,18]
subjects=[6]
fig, axes = plt.subplots(nrows=3, ncols=3,figsize=(20,20))
isub=8
cm = plt.get_cmap('hot') 
cNorm  = colors.Normalize(vmin=0, vmax=3)
scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
predicted=[]
Nsigma=3
for isub in range(len(subjects)):
    
#    filename='/home/gprat/Master Project/meg_analysis/decoding_data/subject_'+str(subjects[isub])+'_matrix.pickle'
    filename='/home/gprat/cluster_archive/Master_Project/results/subject_'+str(subjects[isub])+'_matrix_sigmas.pickle'
    f=open(filename,'r')
#    data = pd.read_pickle(filename)
    data=pickle.load(f)
    result=data['decoding']
    result_err=data['decding_err']

    for isigma in range(len(result)):    
        array_re=np.array(result[isigma])
        array_re_err=np.array(result_err[isigma])
        predicted=[]
        predicted_err=[]

    #    predicted.append(array_re[0,:])
    #    predicted.append(array_re[12,:])
        predicted.append(array_re[25,:])
        predicted_err.append(array_re_err[25,:])
       
        x=np.linspace(-2.5,0.5,len(predicted[0]))
        for i in range(len(predicted)):
            color=scalarMap.to_rgba(isigma)
            axes.flat[isub].errorbar(x,predicted[i],predicted_err[i],fmt='o-',color=color,linewidth=2)
#        axes.flat[isub].plot(x,np.diagonal(array_re),'ro-')
        
        axes.flat[isub].spines['top'].set_visible(False)
        axes.flat[isub].spines['right'].set_visible(False)
        axes.flat[isub].xaxis.set_ticks_position('bottom')
        axes.flat[isub].yaxis.set_ticks_position('left')
        axes.flat[isub].set_ylim(0.25,1)
        axes.flat[isub].set_ylabel('Decoder performance')
        axes.flat[isub].set_xlabel('time (t=0 decision)')
    
plt.show()