import os
import pandas as pd
from attractor import utils
from pymeg import aggregate_sr as asr, parallel


def submit_aggregates(collect=False):
    import numpy as np
    import time

    tasks = []
    subjects = [1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19]
    for subject in subjects:
        for session in [5,6,7,8]:
            for epoch in ['stimulus', 'response']:
                tasks.append([(subject, session, epoch)])
    res = []
    for cnt, task in enumerate(tasks):
        try:
            r = parallel.pmap(
                get_aggregate,
                task,
                walltime="05:30:00",
                tasks=4,
                memory=40,
            )
            res.append(r)
        except RuntimeError:
            print("Task", task, " not available yet")
    return res


def get_aggregate(
    subject, session, epoch="stimulus"
):

    # Load meta!
    

    files = {
        "stimulus": utils.get_filenames(subject, epoch="stimulus", session=session)[1],
        "response": utils.get_filenames(subject, epoch="response", session=session)[1],
        "baseline": utils.get_filenames(subject, epoch="stimulus", session=session)[1],
    }
    
    agg = asr.aggregate_files(
        files[epoch],
        files["baseline"],
        (-0.35, -0.1),
        hemis=["Averaged", "Pair", "Lateralized"],                        
    )
    fname = 'S%i-SESS%i-%s.agg.hdf'%(subject, session, epoch)
    asr.agg2hdf(agg, os.path.join('/home/gortega/preprocessed_megdata/source_space/aggregates', fname))
    return agg

