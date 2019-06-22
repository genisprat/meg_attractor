#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 26 20:27:32 2018

@author: gprat
"""

from pymeg.specific import lcmv_gortega
import os
import glob
import sys
from os.path import join
import re
import pickle
import pandas as pd

path_pymeg='/home/genis/pymeg/'
subject_int=int(sys.argv[1])
session_int=int(sys.argv[2])
block=int(sys.argv[3])

subject='S%i' % (subject_int)


#print('**********************************starting',subject_int,session_int)
print('**********************************starting',subject_int,session_int,block,'******************')
# lcmv_gortega.extract_reconstruct_tfr_block(subject,session_int,block,'stimulus',signal_type='HF')
# lcmv_gortega.extract_reconstruct_tfr_block(subject,session_int,block,'response',signal_type='HF')
lcmv_gortega.extract_reconstruct_tfr_block(subject,session_int,block,'stimulus',signal_type='LF')



print('done',subject,session_int,block)




#lcmv_gortega.extract_reconstruct_tfr("S16",5,0,'response',signal_type='HF')


