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


os.environ["PYMEG_CACHE_DIR"] = "/home/genis/pymeg"


def hash(subject, session, block, trial):
    return subject * 1000000 + session * 10000 + block * 1000 + trial


def eliminate_spurious_columns(df, columns):
    aux_c = []
    for c in df.keys():
        #        print(c,columns,c not in columns)

        if c not in columns:
            aux_c.append(c)

    return df.drop(columns=aux_c)


def interpolate_bad_channels(subject, session, raw):
    if subject == 14 and session == 5:
        raw = raw.load_data()
        raw = raw.drop_channels([u"MLF21-3705"])
        raw = raw.interpolate_bads()

    return raw


def get_blocks(meta, timing):
    """
    Return block start and end times

    """
    blocks = {}
    indices = {}
    for mblock, m in meta.groupby("block_start"):
        # If trial numbers are consecutive all good
        if any(np.diff(m.trial_num) < 0):
            1/0
            # Somehow this block was restarted. Cout out first part of block
            idx = np.where(np.diff(m.trial_num) < 0)[0]
            m = m.iloc[idx[0] + 1 :].trial_num
        tblock = timing.loc[m.index]
        start = tblock.trial_start_time.values.min()
        end = tblock.trial_end_time.values.max()
        blocks[mblock] = (start, end)
        indices[mblock] = (tblock.index.min(), tblock.index.max())
    return blocks, indices


# def run_subject(subject, session):


def submit_all():
    from pymeg import parallel
    # fmt: off
    subjects = [1,4,5,6,7,
        8,9,10,11,12,14,
        15,16,17,18,19,
    ]

    # fmt: on
    for session in [5,6,7]:
        for subject in subjects:
            parallel.pmap(preprocess, [(subject,session)],
                walltime="02:30:00",
                tasks=3,
                memory=30,)



def preprocess(subject, session):
    columns_meta = [
        u"baseline_start",
        u"decision_start",
        u"dot_onset",
        u"feedback",
        u"noise",
        u"response",
        u"rest_delay",
        u"trial_end",
        u"trial_num",
        u"trial_start",
        u"wait_fix",
        u"session_number",
        u"block_start",
    ]

    columns_timing = [
        "baseline_start_time",
        "decision_start_time",
        "dot_onset_time",
        "feedback_time",
        "noise_time",
        "response_time",
        "rest_delay_time",
        "trial_end_time",
        "trial_start_time",
        "wait_fix_time",
    ]

    path = "/mnt/homes/home024/gortega/megdata/"
    path_cluster = "/home/gortega/preprocessed_megdata/sensor_space"
    path_megdata = "/home/gortega/megdata/"

    for file_idx, filename in enumerate(
        glob.glob(os.path.join(path_megdata, "*S%i-%i_Att*" % (subject, session)))
    ):
        date = filename[-14:-6]
        raw = mne.io.read_raw_ctf(filename)
        #raw._first_samps = np.cumsum(raw._raw_lengths) - raw._raw_lengths[0]
        #raw._last_samps = np.cumsum(raw._last_samps)

        ##pins and mapping
        other_pins = {100: "session_number", 101: "block_start"}
        trial_pins = {150: "trial_num"}
        mapping = {
            ("noise", 0): 111,
            ("noise", 1): 112,
            ("noise", 2): 113,
            ("start_button", 0): 89,
            ("start_button", 1): 91,
            ("trial_start", 0): 150,
            ("trial_end", 0): 151,
            ("wait_fix", 0): 30,
            ("baseline_start", 0): 40,
            ("dot_onset", 0): 50,
            ("decision_start", 0): 60,
            ("response", -1): 61,
            ("response", 1): 62,
            ("no_decisions", 0): 68,
            ("feedback", 0): 70,
            ("rest_delay", 0): 80,
        }
        mapping = dict((v, k) for k, v in mapping.items())

        # I get metadata and timing of the raw data.
        meta, timing = preprocessing.get_meta(
            raw, mapping, trial_pins, 150, 151, other_pins
        )
        index = meta.block_start
        block_times, block_idx = get_blocks(meta, timing)

        for bnum in block_times.keys():
            print(
                "******************************** SESSION",
                session,
                "BLOCK",
                bnum,
                "******************************** ",
            )
            
            mb2 = meta.loc[block_idx[bnum][0] : block_idx[bnum][1]]
            tb2 = timing.loc[block_idx[bnum][0] : block_idx[bnum][1]]

            tb2 = tb2.dropna(subset=["dot_onset_time"])
            mb2 = mb2.dropna(subset=["dot_onset"])
            index = []
            for idx in tb2.index:
                try:
                    if len(tb2.loc[idx, "dot_onset_time"]) == 10:
                        index.append(idx)
                        tb2.loc[idx, "first_dot_time"] = tb2.loc[idx, "dot_onset_time"][0]
                        mb2.loc[idx, "first_dot"] = mb2.loc[idx, "dot_onset"][0]
                except TypeError:
                    pass
            tb2 = tb2.loc[index]
            mb2 = mb2.loc[index]

            r = raw.copy()  # created a copy to do not change raw
            r.crop(
                tmin=block_times[bnum][0]/1200, #[tb2.trial_start_time.min() / 1200.0 - 1,
                tmax=block_times[bnum][1]/1200#1 + (tb2.feedback_time.max() / 1200.0),
            )  # crop for each block
            r = interpolate_bad_channels(subject, session, r)
            mb, tb = meg.preprocessing.get_meta(
                r, mapping, trial_pins, 150, 151, other_pins
            )  # get new metadata for each block

            mb = eliminate_spurious_columns(
                mb, columns_meta
            )  # sometime we need to drop some columns
            tb = eliminate_spurious_columns(tb, columns_timing)
            tb = tb.dropna()
            mb = mb.dropna()
            r, ants, artdef = meg.preprocessing.preprocess_block(
                r, blinks=True
            )  # preprocess of each block looking for artifacts

            print("Notch filtering")
            midx = np.where([x.startswith("M") for x in r.ch_names])[0]
            r.load_data()
            r.notch_filter(np.arange(50, 251, 50), picks=midx)

            bad_channels = r.info["bads"]
            if len(r.info["bads"]) > 0:
                r.load_data()
                r.interpolate_bads(reset_bads=False)
                r.info["bads"] = []

            trial_repeat = []
            mb.loc[:, "hash"] = hash(subject, mb.session_number, bnum, mb.trial_num)

            # Create a colum for onset of first dot
            tb.loc[:, 'first_dot_time'] = np.array([x[0] for x in tb.dot_onset_time])
            stimmeta, stimlock = preprocessing.get_epoch(
                r,
                mb.dropna(),
                tb.dropna(),
                event="first_dot_time",
                epoch_time=(-1, 3.5),
                epoch_label="hash",
                reject_time=(0, 2),
            )
            

            if len(stimmeta) > 0:
                stim_filename = join(
                    path_cluster,
                    "down_sample_stim_meta_sub%i_sess%i_block%i_offset%i"
                    % (subject, session, bnum, file_idx),
                )
                stimlock.resample(600, npad="auto")
                stimmeta.to_hdf(stim_filename + ".hdf", "meta")
                stimlock.save(stim_filename + "-epo.fif.gz")

            rlmeta, resplock = preprocessing.get_epoch(
                r,
                mb.dropna(),
                tb.dropna(),
                event="response_time",
                epoch_time=(-2.5, 0.5),
                epoch_label="hash",
                reject_time=(-1, 0.4),
            )
            if len(rlmeta) > 0:
                resp_filename = join(
                    path_cluster,
                    "down_sample_resp_meta_sub%i_sess%i_block%i_offset%i"
                    % (subject, session, bnum, file_idx),
                )
                resplock.resample(600, npad="auto")
                rlmeta.to_hdf(resp_filename + ".hdf", "meta")
                resplock.save(resp_filename + "-epo.fif.gz")

    print("done")
