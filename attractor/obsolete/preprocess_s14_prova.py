#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 11:39:59 2016
preprocess meg data
@author: crm
"""
import meg
import mne
import pickle
import sys
import glob
import os
import numpy as np

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
        return int(str(a)+str(2)),1 #if it already exist then I add a 2 at the end.
    except KeyError:
        x_str=''
        for k in range(len(x)):
            x_str=x_str+str(x[k])
        x_num=int(x_str)
        cache[x2] = x_num

        return cache[x2],0


if __name__ == '__main__':
    subjects=['1','4','5','6','7','8','9','10','11','12','14','15','16','17','18','19']
#    subjects=['1','4','5','6','7','8','9','10','12','14','15','17','18']
    subject=14
    path='/mnt/homes/home024/gortega/megdata/'
    cache={}
    mapname = '/mnt/homes/home024/gortega/meg_analysis/key_maps/key_map_s'+str(subject)+'.pickle'
#    for filename in glob.glob(os.path.join(path, '*S'+str(subject)+'-*')):
    for kj in [1]:
        filename='/mnt/homes/home024/gortega/megdata/S14-5_Attractor_20161115_02.ds'
        aux_aux=True
        raw = mne.io.read_raw_ctf(filename,preload=True)

#        filename='/mnt/homes/home024/gortega/megdata/S14-5_Attractor_20161115_02.ds'
        date=filename[-14:-6]
        
        print filename,date 
        

        
        sesion=5
        subject=14
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
                    
                
        for i, ((bnum, mb), (_, tb)) in enumerate(zip(meta.groupby(index), timing.groupby(index))):
            if bnum==6 and aux_aux:
                print 'drop_channel'
                raw.drop_channels([u'MLF21-3705'])
                r = raw.copy() #created a copy to do not change raw
    #                r.info['bads']=[u'MLF21-3705']
                r.crop(tmin=time_block[i]/1200.0-10, tmax=1+(tb.feedback_time.max()/1200.)) #crop for each block
                print 'getting metadata from raw data form block',i
                mb, tb = meg.preprocessing.get_meta(r, mapping, trial_pins, 150, 151, other_pins) #get new metadata for each block
                print 'metadata done, preprocesing...',mb.session_number[0]
        
                r, ants, artdef = meg.preprocessing.preprocess_block(r, blinks=True) #preprocess of each block looking for artifacts
                #created hash: in thios column I will indentify the for each trial a different number.
                print 'preprocess done'
                trial_repeat=[]
                mb.loc[:,'hash']=1
                for j in mb.index:
                    mb.loc[j,'hash'],aux=hash3([subject, int(mb.session_number[j]),int(bnum),int(mb.trial_num[j]),int(date)])
                    trial_repeat.append(aux)
                #Now i computed the epochs: 1epoch=trial
                    
                rlmeta, resplock = meg.preprocessing.get_epoch(r, mb.dropna(), tb.dropna(), event='response_time', epoch_time=(-2.5, .5),
                        base_event='baseline_start_time', base_time=(0, 0.5), epoch_label='hash') #here I use dropna() because if not the timming is not unique
                
    
                if len(rlmeta)>0:
                    rlmeta.to_hdf('/mnt/homes/home024/gortega/meg_analysis/preprocess_data/resp_meta_sub'+str(subject)+'_s'+str(int(mb.session_number[0]))+'_block'+str(int(mb.block_start[0]))+'.hdf', 'meta')
                    resplock.save('/mnt/homes/home024/gortega/meg_analysis/preprocess_data/resp_sub'+str(subject)+'_s'+str(int(mb.session_number[0]))+'_block'+str(int(mb.block_start[0]))+'-epo.fif.gz')
                    print 'block',bnum,'saved' 
                else:
                    print 'WARNING ALL TRIALS DROP BECAUSE OF ARTIFACTS', subject,bnum
                #statistics of the preprocessing:
                block_stat={}
                block_stat['num_trials']=len(mb)
                block_stat['num_valid_trials']=len(rlmeta)
                block_stat['num_blinks']=len(artdef['blinks'].onset)
                block_stat['num_cars']=len(artdef['cars'])
                block_stat['num_muscle']=len(artdef['muscle'])
                block_stat['num_jumps']=len(artdef['jumps'])
                block_stat['trial_repeat']=trial_repeat
                block_stat['subject']=subject
                block_stat['bnum']=bnum
                block_stat['session']=mb.session_number[0]
        
                file_stat=open('/mnt/homes/home024/gortega/meg_analysis/preprocess_data/resp_bstat_sub'+str(subject)+'_s'+str(int(mb.session_number[0]))+'_block'+str(int(mb.block_start[0]))+'.pickle','w')
                pickle.dump(block_stat,file_stat)


    f=open(mapname,'w')
    pickle.dump(cache, f)
    f.close()
    


