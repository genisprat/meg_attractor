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
cm = plt.get_cmap('winter') 
cNorm  = colors.Normalize(vmin=0, vmax=1)
scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
predicted=[]
path='/home/genis/cluster_archive/Master_Project/meg_analysis/results'
for isub in range(len(subjects)):
    
    filename=path+'/subject_'+str(subjects[isub])+'_matrix.pickle'
    f=open(filename,'r')
    data=pickle.read(filename)
#    result = pd.read_pickle(filename)
#    
#    array_re=np.array(result)
#    predicted=[]
#    predicted.append(array_re[0,:])
##    predicted.append(array_re[12,:])
#    predicted.append(array_re[25,:])
#   
#    x=np.linspace(-2.5,0.5,len(predicted[0]))
#    for i in range(len(predicted)):
#        color=scalarMap.to_rgba(i)
#        axes.flat[isub].plot(x,predicted[i],'o-',color=color)
#    axes.flat[isub].plot(x,np.diagonal(array_re),'ro-')
#    
#    axes.flat[isub].spines['top'].set_visible(False)
#    axes.flat[isub].spines['right'].set_visible(False)
#    axes.flat[isub].xaxis.set_ticks_position('bottom')
#    axes.flat[isub].yaxis.set_ticks_position('left')
#    axes.flat[isub].set_ylim(0.25,1)
#    axes.flat[isub].set_ylabel('Decoder performance')
#    axes.flat[isub].set_xlabel('time (t=0 decision)')
#    
#plt.show()