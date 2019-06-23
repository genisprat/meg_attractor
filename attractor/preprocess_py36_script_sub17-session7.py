#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 11:39:59 2016
preprocess meg data
@author: crm
"""
import pymeg as meg
from pymeg import preprocessing
import mne
import pickle
import sys
import glob
import os
import numpy as np
import time
from os.path import join
import glob


os.environ["PYMEG_CACHE_DIR"]="~/pymeg"

def hash2(x,cache):

    x = tuple(x)
    try:
        
        return cache[x]
    except KeyError:
        cache[x] = max(cache.values())+1
        f=open(mapname,'w')
        pickle.dump(cache, f)
        f.close()
        return cache[x]

def hash3(x):
    x2 = tuple(x)
    try:
        a=cache[x2]
        x_num=int(str(a)+str(2))
        x.append(2)
        x2 = tuple(x)
        cache[x2]=x_num
        return x_num,1 #if it already exist then I add a 2 at the end.
    except KeyError:
        x_str=''
        for k in range(len(x)):
            x_str=x_str+str(x[k])
        x_num=int(x_str)
        cache[x2] = x_num

        return cache[x2],0

def hash4(x):
    x.append(0) #last 0 means no repetiotion
    x2 = tuple(x)
    if len(cache)==0:
        sub=int(x[0])
        x_num=sub*10000
        cache[x2]=x_num
        return x_num,0
    try:
        x_num=max(cache.values())+1
        x[-1]=x[-1]+1#if it already exist then I add a 1 at the end.
        x2=tuple(x)
        cache[x2]=x_num
        return x_num,1 
    except KeyError:
        x_num=max(cache.values())+1
        cache[x2] = x_num

        return cache[x2],0
    
    
def eliminate_spurious_columns(df,columns):
    aux_c=[]
    for c in df.keys():
#        print(c,columns,c not in columns)
        
        if c not in columns:
            aux_c.append(c)
            
    return df.drop(columns=aux_c)

def interpolate_bad_channels(subject,session,raw):
    if subject==14 and session==5:
        raw=raw.load_data()
        raw=raw.drop_channels([u'MLF21-3705'])
        raw=raw.interpolate_bads()
        
    return raw
    
    


#def run_subject(subject, session):

if __name__ == '__main__':
    print('putas todos')
    print(sys.argv)
    subjects=['1','4','5','6','7','8','9','10','11','12','14','15','16','17','18','19']
#    subject=int(subjects[int(sys.argv[1])])
    subject=int(sys.argv[1])
    session=int(sys.argv[2])
#    path='/mnt/homes/home024/gortega/megdata/' 
    path='/media/genis/megdata/' # path cluster Barcelona   

    print('subject:',subject, 'session',session)    
    
    
    columns_meta=[u'baseline_start', u'decision_start', u'dot_onset', u'feedback', u'noise', 
             u'response', u'rest_delay', u'trial_end', u'trial_num', u'trial_start',
             u'wait_fix', u'session_number', u'block_start']

    columns_timing=['baseline_start_time', 'decision_start_time', 'dot_onset_time',
       'feedback_time', 'noise_time', 'response_time', 'rest_delay_time',
       'trial_end_time', 'trial_start_time', 'wait_fix_time']
    
    global cache
#    path_cluster='/home/gortega/preprocessed_megdata/'    
#    path_megdata = '/home/gortega/megdata/'
    
    path_megdata='/media/genis/megdata/'
    path_cluster='/media/genis/preprocessed_megdata/'    

    mapname = path_cluster + 'key_map_s'+str(subject)+'.pickle'
    
    try:
        f=open(mapname,'rb')
        cache=pickle.load(f)
    except:
        cache={}
        
        
    for file_idx, filename in enumerate(glob.glob(os.path.join( path_megdata, '*S%i-%i_Att*'%(subject, session)))):
#        filename=path_megdata+'S17-7_Attractor_20161130_02.ds'
        date=filename[-14:-6]        
        raw = mne.io.read_raw_ctf(filename)
    
        ##pins and mapping
        other_pins = {100:'session_number',
                101:'block_start'}
        
        trial_pins = {150:'trial_num'}
        
        mapping = {
               ('noise', 0):111,
               ('noise', 1):112,
               ('noise', 2):113,
               ('start_button', 0):89,
               ('start_button', 1):91,
               ('trial_start', 0):150,
               ('trial_end', 0):151,
               ('wait_fix', 0):30,
               ('baseline_start',0):40,
               ('dot_onset',0):50,
               ('decision_start',0) : 60,
               ('response',-1) : 61,
               ('response', 1) : 62,
               ('no_decisions',0) : 68,
               ('feedback', 0) : 70,
               ('rest_delay',0) : 80}
        
        mapping = dict((v,k) for k,v in mapping.items())
        #    I created the key_map to give a number to each trial.
        
        
        #I get metadata and timing of the raw data.        
        meta,timing = preprocessing.get_meta(raw, mapping, trial_pins, 150, 151, other_pins) 
        index = meta.block_start
        
        #I separate the raw data by blocks
        #time where the block start
        events=mne.find_events(raw, 'UPPT001', shortest_event=1)
        index_b_start=np.where(events[:,2]==100)#block start on every trigger 100
        time_block=[]
        time_block2=[]
        for i in index_b_start[0]:
            time_block.append(events[i][0])
        if len(meta.groupby('block_start'))==len(time_block):
            pass
        else:
            if filename==path_megdata+'S17-7_Attractor_20161130_01.ds': ####here I solve the problem with subject17
                time_block.remove(time_block[2])
                print('remove rime_block2')
            
            for i in range(len(time_block)-1):
                ii=timing[timing['baseline_start_time']>time_block[i]].index[2]
                jj=timing[timing['baseline_start_time']>time_block[i+1]].index[2]
                if meta['block_start'][ii]==meta['block_start'][jj]:
                    time_block2.append(time_block[i+1])
        for i in range(len(time_block2)):
            time_block.remove(time_block2[i])
                    

        for i, ((bnum, mb), (_, tb)) in enumerate(zip(meta.groupby(index), timing.groupby(index))):
            print('******************************** SESSION',session,'BLOCK',bnum,'******************************** ')
            # Filter out incomplete trials
            total_trials=len(mb)
            tb = tb.dropna(subset=['dot_onset_time'])
            mb = mb.dropna(subset=['dot_onset'])
            index = []
            total_trials=len(mb)
            for idx in tb.index:
                try:
                    if len(tb.loc[idx, 'dot_onset_time']) == 10:
                        index.append(idx)
                        tb.loc[idx, 'first_dot_time'] = tb.loc[idx, 'dot_onset_time'][0]
                        mb.loc[idx, 'first_dot'] = mb.loc[idx, 'dot_onset'][0]
                except TypeError:
                    pass
            tb = tb.loc[index]
            mb = mb.loc[index]
            
            r = raw.copy() #created a copy to do not change raw
            r.crop(tmin=time_block[i]/1200.0-10, tmax=1+(tb.feedback_time.max()/1200.)) #crop for each block
            r=interpolate_bad_channels(subject,session,r)
            mb, tb = meg.preprocessing.get_meta(r, mapping, trial_pins, 150, 151, other_pins) #get new metadata for each block  
            
            mb=eliminate_spurious_columns(mb,columns_meta) #sometime we need to drop some columns
            tb=eliminate_spurious_columns(tb,columns_timing)                   
            
            r, ants, artdef = meg.preprocessing.preprocess_block(r, blinks=True) #preprocess of each block looking for artifacts
            #created hash: in thios column I will indentify the for each trial a different number.

            # Filter out incomplete trials
            tb = tb.dropna(subset=['dot_onset_time'])
            mb = mb.dropna(subset=['dot_onset'])
            index = []
            for idx in tb.index:
                try:
                    if len(tb.loc[idx, 'dot_onset_time']) == 10:
                        index.append(idx)
                        tb.loc[idx, 'first_dot_time'] = tb.loc[idx, 'dot_onset_time'][0]
                        mb.loc[idx, 'first_dot'] = mb.loc[idx, 'dot_onset'][0]
                except TypeError:
                    pass
            tb = tb.loc[index]
            mb = mb.loc[index]


            bad_channels=r.info['bads']
            if len(r.info['bads'])>0:
              r.load_data()
              r.interpolate_bads(reset_bads=False)
              r.info['bads']=[]
        
            trial_repeat=[]
            mb.loc[:,'hash']=1
            for j in mb.index:
                mb.loc[j,'hash'],aux=hash4([subject, int(mb.session_number[j]),int(bnum),int(mb.trial_num[j]),int(date)])
                trial_repeat.append(aux)
            #Now i computed the epochs: 1epoch=trial
            
            stimmeta, stimlock = preprocessing.get_epoch(r, mb.dropna(), tb.dropna(), 
                                                       event='first_dot_time', epoch_time=(-1, 3.5),                                                       
                                                       epoch_label='hash',reject_time=(0, 2))  
            session_number=int(mb.session_number[mb.index[0]])
            block_number=int(mb.block_start[mb.index[0]])
            if len(stimmeta)>0:
                
                stim_filename = join(path_cluster, 
                                     'down_sample_stim_meta_sub%i_sess%i_block%i_offset%i'%(subject, session_number, block_number,
                                                                                file_idx))
                stimlock.resample(600, npad="auto") 
                stimmeta.to_hdf(stim_filename + '.hdf', 'meta')
                stimlock.save(stim_filename + '-epo.fif.gz')       

                            
            rlmeta, resplock = preprocessing.get_epoch(r, mb.dropna(), tb.dropna(), 
                                                       event='response_time', epoch_time=(-2.5, .5),
                                                       epoch_label='hash',reject_time=(-1, 0.4))     
            if len(rlmeta)>0:                
                resp_filename = join(path_cluster, 
                                     'down_sample_resp_meta_sub%i_sess%i_block%i_offset%i'%(subject, session_number, block_number,
                                                                                file_idx))
                resplock.resample(600, npad="auto")
                rlmeta.to_hdf(resp_filename + '.hdf', 'meta')
                resplock.save(resp_filename + '-epo.fif.gz')
                
                
            ##statistics of the preprocessing:
            block_stat={}
            block_stat['num_trials']=total_trials
            block_stat['finish_trials']=len(mb)
            block_stat['num_valid_trials_stim']=len(stimlock)
            block_stat['num_valid_trials_resp']=len(resplock)
            block_stat['num_blinks']=list(ants.description).count('bad blinks')
            block_stat['num_cars']=list(ants.description).count('bad car')
            block_stat['num_muscle']=list(ants.description).count('bad muscle')
            block_stat['num_jumps']=list(ants.description).count('bad jump')
            block_stat['trial_repeat']=trial_repeat
            block_stat['subject']=subject
            block_stat['bnum']=bnum
            block_stat['session']=session_number
            block_stat['bad_channels']=bad_channels
            file_stat=open(path_cluster+'/resp_bstat_sub'+str(subject)+'_s'+str(session_number)+'_block'+str(block_number)+'.pickle','wb')
            pickle.dump(block_stat,file_stat)
            file_stat.close()
            
            file_stat=open(path_cluster+'/resp_artifacts_sub'+str(subject)+'_s'+str(session_number)+'_block'+str(block_number)+'.pickle','wb')
            artifact={}
            artifact['ants']=ants
            artifact['artdef']=artdef
            pickle.dump(artifact,file_stat)  
            file_stat.close()
            
            
        f=open(mapname,'wb')
        pickle.dump(cache, f)
        f.close()

    print('done')
    


