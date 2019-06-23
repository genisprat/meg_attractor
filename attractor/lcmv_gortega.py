import logging
import mne
import numpy as np
import os

from joblib import Memory

from os import makedirs
from os.path import join
from glob import glob

from pymeg import lcmv
from pymeg import preprocessing
from pymeg import source_reconstruction as sr
import pandas as pd
import pickle
import sys

#memory = Memory(cachedir=os.environ['PYMEG_CACHE_DIR'])
#path = '/home/gprat/cluster_archive/Master_Project/preprocessed_megdata'
path = '/storage/genis/preprocessed_megdata'
path='/home/gortega/preprocessed_megdata'


def set_n_threads(n):
    import os
    os.environ['OPENBLAS_NUM_THREADS'] = str(n)
    os.environ['MKL_NUM_THREADS'] = str(n)
    os.environ['OMP_NUM_THREADS'] = str(n)


subjects = {}


def submit():
    from pymeg import parallel
    for subject, tasks in subjects.items():
        for session, recording in tasks:
            for signal in ['BB', 'HF', 'LF']:
                parallel.pmap(
                    extract, [(subject, session, recording, signal)],
                    walltime='15:00:00', memory=50, nodes=1, tasks=4,
                    name='SR' + str(subject) + '_' +
                    str(session) + str(recording),
                    ssh_to=None, env='mne')


def lcmvfilename(subject, session, signal, recording, epoch, chunk=None):
    try:
        makedirs(path)
    except:
        pass
    if chunk is None:
        filename = '%s-SESS%i-%s-%i-%s-lcmv.hdf' % (
            subject, session, epoch, recording, signal)
    else:
        filename = '%s-SESS%i-%s-%i-%s-chunk%i-lcmv.hdf' % (
            subject, session, epoch, recording, signal, chunk)
    return join(path+'/source', filename)

def lcmvfilename_block(subject, session, block, signal, recording, epoch, chunk=None):
    try:
        makedirs(path)
    except:
        pass
    if chunk is None:
        filename = '%s-SESS%i-b%i-%s-%i-%s-lcmv.hdf' % (
            subject, session, block, epoch, recording, signal)
    else:
        filename = '%s-SESS%i-b%i-%s-%i-%s-chunk%i-lcmv.hdf' % (
            subject, session,block, epoch, recording, signal, chunk)
    return join(path+'/source', filename)


def get_filenames_block(subject, session, block, recording):
    subject_int=int(subject[1:])


#    for b in blocks:
#        stimulus.append( path+'/stim_meta_sub%i_sess%i_block%i_offset*-epo.fif.gz' % (subject, session,b))
#        response.append( path+'/resp_meta_sub%i_sess%i_block%i_offset*-epo.fif.gz' % (subject, session,b))              

    stimulus=glob(join(path+'/sensor_space', 'down_sample_stim_meta_sub%i_sess%i_block%i_offset*-epo.fif.gz' % (subject_int,session,block)))
    response=glob(join(path+'/sensor_space', 'down_sample_resp_meta_sub%i_sess%i_block%i_offset*-epo.fif.gz' % (subject_int,session,block)))

    return stimulus, response



def get_filenames(subject, session, recording):
    subject_int=int(subject[1:])
    # fname='filenames_sub%i.pickle'% (subject_int)
    fname=path+'filenames_sub%i.pickle'% (subject_int)
    f=open(fname,'rb')
    data=pickle.load(f)
    df=pd.DataFrame.from_dict(data)
    blocks=df[df.subject==subject_int][df.session==session][df.trans_matrix==recording].block
    stimulus=[]
    response=[]
#    for b in blocks:
#        stimulus.append( path+'/stim_meta_sub%i_sess%i_block%i_offset*-epo.fif.gz' % (subject, session,b))
#        response.append( path+'/resp_meta_sub%i_sess%i_block%i_offset*-epo.fif.gz' % (subject, session,b))              

    stimulus=join(path, 'down_sample_stim_meta_sub%i_sess%i_block[%i-%i]_offset*-epo.fif.gz' % (subject_int,session,int(blocks.min()),int(blocks.max())))
    response=join(path, 'down_sample_resp_meta_sub%i_sess%i_block[%i-%i]_offset*-epo.fif.gz' % (subject_int,session,int(blocks.min()),int(blocks.max())))


    return stimulus, response


def get_filename_trans_matrix(subject, session, recording):
    subject_int=int(subject[1:])
    if recording==0:
        b=2
    elif recording==1:
        b=5
    elif recording==2:
        b=7
        
    stimulus=glob(join(path+'/sensor_space', 'down_sample_stim_meta_sub%i_sess%i_block%i_offset*-epo.fif.gz' % (subject_int,session,b)))[0]


    return stimulus


def get_stim_epoch(subject, session, recording):
    filenames = glob(get_filenames(subject, session, recording)[0])
    epochs = preprocessing.load_epochs(filenames)
    
    epochs=preprocessing.concatenate_epochs(epochs,None)
    epochs = epochs.pick_channels(
        [x for x in epochs.ch_names if x.startswith('M')])
    
#    epochs.resample(500, npad="auto")
    print(epochs.info)
    
    id_time = (-0.25 <= epochs.times) & (epochs.times <= 0)
    means = epochs._data[:, :, id_time].mean(-1)
    epochs._data -= means[:, :, np.newaxis]
    
    data_cov = lcmv.get_cov(epochs, tmin=0, tmax=3)
    return data_cov, epochs, filenames


def get_response_epoch(subject, session, recording):
    stimulus = glob(get_filenames(subject, session, recording)[0])
    response = glob(get_filenames(subject, session, recording)[1])
    
    stimulus = preprocessing.load_epochs(stimulus)
    stimulus=preprocessing.concatenate_epochs(stimulus,None)
    stimulus = stimulus.pick_channels(
        [x for x in stimulus.ch_names if x.startswith('M')])
    response = preprocessing.load_epochs(response)
    response=preprocessing.concatenate_epochs(response,None)
    response = stimulus.pick_channels(
        [x for x in response.ch_names if x.startswith('M')])
    print(stimulus.info)
    print(response.info)
#    response.resample(500, npad="auto")
#    stimulus.resample(500, npad="auto")
    
    id_time = (-0.25 <= stimulus.times) & (stimulus.times <= 0)
    means = stimulus._data[:, :, id_time].mean(-1)
    stimulus._data = stimulus._data - means[:, :, np.newaxis]
    response._data = response._data - means[:, :, np.newaxis]
    data_cov = lcmv.get_cov(stimulus, tmin=0, tmax=3)
    filenames = glob(get_filenames(subject, session, recording)[1])
    return data_cov, response,filenames



def extract_reconstruct_tfr(subject, session,recording, epoch, signal_type='BB',
            BEM='three_layer', debug=False, chunks=50, njobs=4):
    
    if epoch=='stimulus':    
        filenames = glob(get_filenames(subject, session, recording)[0])
    else:
        filenames = glob(get_filenames(subject, session, recording)[1])
        
        
    
    subject_int=int(subject[1:])
    fname='filter_sub%i_SESS%i_recording%i_epoch%s.pickle'%( subject_int,session,recording,epoch)
    filename = join(path+'/extra', fname)
    f=open(filename,'rb')
    filters=pickle.load(f)
    f.close()
    fois_h = np.arange(36, 162, 4)
    fois_l = np.arange(2, 36, 1)
    tfr_params = {
    'HF': {'foi': fois_h, 'cycles': fois_h * 0.25, 'time_bandwidth': 2 + 1,
           'n_jobs': njobs, 'est_val': fois_h, 'est_key': 'HF', 'sf': 600,
           'decim': 10},
    'LF': {'foi': fois_l, 'cycles': fois_l * 0.4, 'time_bandwidth': 1 + 1,
           'n_jobs': njobs, 'est_val': fois_l, 'est_key': 'LF', 'sf': 600,
           'decim': 10}
    }
    
    
    print('filters done')
    for ifname,fname in enumerate(filenames):
        print(fname)
        epochs=preprocessing.load_epochs([fname])       
        epochs=preprocessing.concatenate_epochs(epochs,None)
        epochs = epochs.pick_channels([x for x in epochs.ch_names if x.startswith('M')])   
        events = epochs.events[:, 2]
        
        for i in range(0, len(events), chunks):
            print('chunk:',i)
            filename = lcmvfilename(
                subject, session, signal_type, recording,epoch+str(ifname), chunk=i)
            if os.path.isfile(filename):
                continue
            if signal_type == 'BB':
                logging.info('Starting reconstruction of BB signal')
                M = lcmv.reconstruct_broadband(
                    filters, epochs.info, epochs._data[i:i + chunks],
                    events[i:i + chunks],
                    epochs.times, njobs=1)
            else:
                logging.info('Starting reconstruction of TFR signal')
                M = lcmv.reconstruct_tfr(
                    filters, epochs.info, epochs._data[i:i + chunks],
                    events[i:i + chunks], epochs.times,
                    est_args=tfr_params[signal_type],
                    njobs=1)
            M.to_hdf(filename, 'epochs')
            del M
        del epochs
        print('done')



@memory.cache()
def extract_filter(subject, session, recording, epoch, signal_type='BB',
            BEM='three_layer', debug=False, chunks=50, njobs=4):
    mne.set_log_level('WARNING')
    lcmv.logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().setLevel(logging.INFO)
    set_n_threads(1)
    subject_int=int(subject[1:])
    print('reading stimulus data')
    MRI_subjects=["S1","S5","S6","S8","S11","S12","S16","S17"]
    if subject in MRI_subjects:
        subject2=subject
    else:
        subject2="fsaverage"
    
    
    logging.info('Reading stimulus data')

    if epoch == 'stimulus':
        data_cov, epochs, epochs_filename = get_stim_epoch(
            subject, session, recording)
    else:
        data_cov, epochs, epochs_filename = get_response_epoch(
            subject, session, recording)


    fname='/storage/genis/preprocessed_megdata/filenames_sub%i.pickle'% (subject_int)
    f=open(fname,'rb')
    data=pickle.load(f)
    df=pd.DataFrame.from_dict(data)
    raw_filename=df[df.subject==subject_int][df.session==session][df.trans_matrix==recording].filename.iloc[0]
    print('hola')
#    trans_filename = '/home/gprat/cluster_home/pymeg/S%i-sess%i-%i-trans.fif' % (subject_int, session, recording)
    trans_filename = '/home/genis/pymeg/S%i-sess%i-%i-trans.fif' % (subject_int, session, recording)

        
    print('data_cov_done')


    
#    raw_filename = glob('TODO' % (subject, session, recording))

#    trans_filename = glob('TODO' % (subject, session, recording))[0]
    logging.info('Setting up source space and forward model')
    epo_filename=get_filename_trans_matrix(subject, session, recording)
    forward, bem, source = sr.get_leadfield(
        subject2, raw_filename, epo_filename, trans_filename,
        bem_sub_path='bem_ft')
    labels = sr.get_labels(subject2)
    labels = sr.labels_exclude(labels, exclude_filters=['wang2015atlas.IPS4',
                                                        'wang2015atlas.IPS5',
                                                        'wang2015atlas.SPL',
                                                        'JWDG_lat_Unknown'])
    labels = sr.labels_remove_overlap(
        labels, priority_filters=['wang', 'JWDG'],)




    filters = lcmv.setup_filters(epochs.info, forward, data_cov,
                                 None, labels)
    subject_int=int(subject[1:])
    fname='filter_sub%i_SESS%i_recording%i_epoch%s.pickle'%( subject_int,session,recording,epoch)
    filename = join(path, fname)
    f=open(filename,'wb')
    pickle.dump(filters,f)
    print('filter_done')
    f.close()    
    
    return filters



def extract_reconstruct_tfr_block(subject, session, block, epoch, signal_type='BB',
            BEM='three_layer', debug=False, chunks=50, njobs=4):
    

    #check if the block exists and recording
    subject_int=int(subject[1:])
    fname=path+'/filenames_sub%i.pickle'% (subject_int)
    f=open(fname,'rb')
    data=pickle.load(f)
    df=pd.DataFrame.from_dict(data)
    blocks=np.array(df[df.subject==subject_int][df.session==session].block)
    if block in blocks:
        recording=df[df.subject==subject_int][df.session==session][df.block==block].trans_matrix.iloc[0]
    else:
        print('block does not exist')
        sys.exit(0)

    if epoch=='stimulus':    
        fname = get_filenames_block(subject, session, block, recording)[0][0]
    else:
        fname = get_filenames_block(subject, session, block, recording)[1][0]
        
    
    
    
    # fname_aux='filter_sub%i_SESS%i_recording%i_epoch%s.pickle'%( subject_int,session,recording,epoch)
    # filename = join(path+'/extra', fname_aux)
    # f=open(filename,'rb')
    # filters=pickle.load(f)
    # f.close()

    filters=extract_filter(subject,session_int,recording,epoch,signal_type=signal_type)
    fois_h = np.arange(36, 162, 4)
    fois_l = np.arange(2, 36, 1)
    tfr_params = {
    'HF': {'foi': fois_h, 'cycles': fois_h * 0.25, 'time_bandwidth': 2 + 1,
           'n_jobs': njobs, 'est_val': fois_h, 'est_key': 'HF', 'sf': 600,
           'decim': 10},
    'LF': {'foi': fois_l, 'cycles': fois_l * 0.4, 'time_bandwidth': 1 + 1,
           'n_jobs': njobs, 'est_val': fois_l, 'est_key': 'LF', 'sf': 600,
           'decim': 10}
    }
    
    

    print(fname)
    print('loading data')
    epochs=preprocessing.load_epochs([fname])
    print('concataneiting data')       
    epochs=preprocessing.concatenate_epochs(epochs,None)
    print('Picking pick_channels')
    epochs = epochs.pick_channels([x for x in epochs.ch_names if x.startswith('M')])

    events = epochs.events[:, 2]
    
    for i in range(0, len(events), chunks):
        print('chunk:',i)
        filename = lcmvfilename_block(
            subject, session,block, signal_type, recording,epoch, chunk=i)
        if os.path.isfile(filename):
            continue
        if signal_type == 'BB':
            logging.info('Starting reconstruction of BB signal')
            M = lcmv.reconstruct_broadband(
                filters, epochs.info, epochs._data[i:i + chunks],
                events[i:i + chunks],
                epochs.times, njobs=1)
        else:
            logging.info('Starting reconstruction of TFR signal')
            M = lcmv.reconstruct_tfr(
                filters, epochs.info, epochs._data[i:i + chunks],
                events[i:i + chunks], epochs.times,
                est_args=tfr_params[signal_type],
                njobs=1)
        M.to_hdf(filename, 'epochs')
        del M
    del epochs
    print('done')





