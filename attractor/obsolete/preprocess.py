#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 11:39:59 2016
preprocess meg data
@author: crm
"""
import pymeg as meg
import mne
import pickle
import sys
import glob
import os
import numpy as np
import time
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
        print x,'already exist',cache[x2],date,filename
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
        print cache[x2]

        print x,'already exist',cache[x2],date,max(cache.values())
        x_num=max(cache.values())+1
        print x_num
        x[-1]=x[-1]+1#if it already exist then I add a 1 at the end.
        x2=tuple(x)
        cache[x2]=x_num
        return x_num,1 
    except KeyError:
        x_num=max(cache.values())+1
        cache[x2] = x_num

        return cache[x2],0


if __name__ == '__main__':
#    subjects=['1','4','5','6','7','8','9','10','11','12','14','15','16','17','18','19']
#    subjects=['5','6','8','9','10','11','12','15','16','18']
    subjects=['7','9']
    subject=int(subjects[int(sys.argv[1])])
#    subject=7
    cache={}
    path_cluster='/mnt/genis/Master_Project/'
    path_local='/home/genis/cluster_archive/Master_Project/'
    path=path_local
    path_megdata=path+'megdata/'
    
    mapname = path+'meg_analysis/key_maps/key_map_s'+str(subject)+'.pickle'
    t_i=time.time()
    for filename in glob.glob(os. path.join( path_megdata, '*S'+str(subject)+'-*')):
#    for ii in [1]:
#        filename=path_local+'megdata/S1-7_Attractor_20161025_01.ds'
        date=filename[-14:-6]
        print filename,date 
        raw = mne.io.read_raw_ctf(filename)
        
#        sesion=7
#        date=20161129
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
               ('response',1) : 62,
               ('no_decisions',0) : 68,
               ('feedback',0) : 70,
               ('rest_delay',0) : 80}
        
        mapping = dict((v,k) for k,v in mapping.iteritems())
    #    I created the key_map to give a number to each trial.
        
        
        #I get metadata and timing of the raw data.
        print 'get metadata from raw data'
        meta,timing=meg.preprocessing.get_meta(raw, mapping, trial_pins, 150, 151, other_pins) 
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
            for i in range(len(time_block)-1):
                ii=timing[timing['baseline_start_time']>time_block[i]].index[2]
                jj=timing[timing['baseline_start_time']>time_block[i+1]].index[2]
                if meta['block_start'][ii]==meta['block_start'][jj]:
                    time_block2.append(time_block[i+1])
        for i in range(len(time_block2)):
            time_block.remove(time_block2[i])
                    
        print 'blocks: ',meta.block_start.unique()
        for i, ((bnum, mb), (_, tb)) in enumerate(zip(meta.groupby(index), timing.groupby(index))):
            r = raw.copy() #created a copy to do not change raw
            r.crop(tmin=time_block[i]/1200.0-10, tmax=1+(tb.feedback_time.max()/1200.)) #crop for each block
            print 'getting metadata from raw data form block',i
            mb, tb = meg.preprocessing.get_meta(r, mapping, trial_pins, 150, 151, other_pins) #get new metadata for each block
            print 'metadata done, preprocesing...',mb.session_number[0]
            
            r, ants, artdef = meg.preprocessing.preprocess_block(r, blinks=True) #preprocess of each block looking for artifacts
            #created hash: in thios column I will indentify the for each trial a different number.

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
               
            rlmeta, resplock = meg.preprocessing.get_epoch(r, mb.dropna(), tb.dropna(), event='response_time', epoch_time=(-2.5, .5),
                    base_event='baseline_start_time', base_time=(0, 0.5), epoch_label='hash') #here I use dropna() because if not the timming is not unique
            
            print 'aaaa_session: ',mb.session_number[0], 'block:',mb.block_start[0] 
            if len(rlmeta)>0:
                rlmeta.to_hdf(path+'process_data/resp_meta_sub'+str(subject)+'_s'+str(int(mb.session_number[0]))+'_block'+str(int(mb.block_start[0]))+'.hdf', 'meta')
                resplock.save(path+'process_data/resp_sub'+str(subject)+'_s'+str(int(mb.session_number[0]))+'_block'+str(int(mb.block_start[0]))+'-epo.fif.gz')
                print 'block',bnum,'saved' 
            else:
                print 'WARNING ALL TRIALS DROP BECAUSE OF ARTIFACTS', subject,bnum
            if len(rlmeta)!=len(resplock):
                print "WARNING len meta and len resplock different"
            ##statistics of the preprocessing:
            block_stat={}
            block_stat['num_trials']=len(mb)
            block_stat['num_valid_trials']=len(rlmeta)
            block_stat['num_blinks']=list(ants.description).count('bad blinks')
            block_stat['num_cars']=list(ants.description).count('bad car')
            block_stat['num_muscle']=list(ants.description).count('bad muscle')
            block_stat['num_jumps']=list(ants.description).count('bad jump')
            block_stat['trial_repeat']=trial_repeat
            block_stat['subject']=subject
            block_stat['bnum']=bnum
            block_stat['session']=mb.session_number[0]
            block_stat['bad_channels']=bad_channels
            file_stat=open(path+'process_data/resp_bstat_sub'+str(subject)+'_s'+str(int(mb.session_number[0]))+'_block'+str(int(mb.block_start[0]))+'.pickle','w')
            pickle.dump(block_stat,file_stat)
            file_stat.close()
            
            file_stat=open(path+'process_data/resp_artifacts_sub'+str(subject)+'_s'+str(int(mb.session_number[0]))+'_block'+str(int(mb.block_start[0]))+'.pickle','w')
            artifact={}
            artifact['ants']=ants
            artifact['artdef']=artdef
            pickle.dump(artifact,file_stat)  
            file_stat.close()
            
            
    f=open(mapname,'wb')
    pickle.dump(cache, f)
    f.close()

print 'all_done',(time.time()-t_i)/60.0
    


