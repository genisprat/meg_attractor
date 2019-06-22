import os
import pandas as pd
from attractor import utils
from pymeg.contrast_tfr import Cache, compute_contrast, augment_data

import logging
from joblib import Memory

memory = Memory(location=os.environ["PYMEG_CACHE_DIR"], verbose=0)


contrasts = {
    "all": (["all"], [1]),
    
    #"choice": (["hit", "fa", "miss", "cr"], (1, 1, -1, -1)),
    #"stimulus": (["hit", "fa", "miss", "cr"], (1, -1, 1, -1)),
    #"hand": (["left", "right"], (1, -1)),
}


#@memory.cache()
def get_contrasts(
    contrasts, subject, epochs=["stimulus", "response"], baseline_per_condition=False
):
    #hemis = ['lh_is_ipsi', "avg"]

    # Load meta!
    meta = utils.get_meta(subject)
    new_contrasts = {}
    for key, value in contrasts.items():
        new_contrasts[key + "lat"] = [value[0], value[1], 'lh_is_ipsi']
        new_contrasts[key + "avg"] = [value[0], value[1], "avg"]
    contrasts = new_contrasts

    files = {'stimulus': utils.get_filenames(subject, epoch="stimulus")[1],
              'response':utils.get_filenames(subject, epoch="response")[1],
              'baseline': utils.get_filenames(subject, epoch="stimulus")[1]}

    response_left = meta.response == 1
    left_correct = meta.response == 1 #!TODO!
    meta = augment_data(meta, response_left, left_correct)

    cps = []
    with Cache() as cache:
        for epoch in epochs:
            try:
                contrast = compute_contrast(
                    contrasts,
                    files[epoch],
                    files['baseline'],
                    meta,
                    (-0.35, -0.1),
                    baseline_per_condition=baseline_per_condition,
                    n_jobs=1,
                    cache=cache,
                )
                contrast.loc[:, "epoch"] = epoch
                cps.append(contrast)
            except ValueError as e:
                print(e)
                pass

    contrast = pd.concat(cps)
    del cps
    contrast.loc[:, "subject"] = subject

    contrast.set_index(
        ["subject", "contrast", "hemi", "epoch", "cluster"], append=True, inplace=True
    )
    return contrast


def submit_contrasts(collect=False):
    pass


def _eval(func, args, collect=False, **kw):
    """
    Intermediate helper to toggle cluster vs non cluster
    """
    if not collect:
        if not func.in_store(*args):
            print("Submitting %s to %s for parallel execution" % (len(args), func))
            parallel.pmap(func, [args], **kw)
    else:
        if func.in_store(*args):
            print("Submitting %s to %s for collection" % (str(args), func))
            df = func(*args)
            return df
        else:
            raise RuntimeError("Result not available.")


def submit_stats(
    contrasts=["all", "choice", "confidence", "confidence_asym", "hand", "stimulus"],
    collect=False,
):
    all_stats = {}
    tasks = []
    for contrast in contrasts:
        for hemi in [True, False]:
            for epoch in ["stimulus", "response"]:
                tasks.append((contrast, epoch, hemi))
    res = []
    for task in tasks[:]:
        try:
            r = _eval(
                precompute_stats,
                task,
                collect=collect,
                walltime="08:30:00",
                tasks=2,
                memory=20,
            )
            res.append(r)
        except RuntimeError:
            print("Task", task, " not available yet")
    return res


@memory.cache()
def precompute_stats(contrast, epoch, hemi):
    from pymeg import atlas_glasser

    df = pd.read_hdf(
        "/home/nwilming/conf_analysis/results/all_contrasts_confmeg-20190516.hdf"
    )
    if epoch == "stimulus":
        time_cutoff = (-0.5, 1.35)
    else:
        time_cutoff = (-1, 0.5)
    query = 'epoch=="%s" & contrast=="%s" & %s(hemi=="avg")' % (
        epoch,
        contrast,
        {True: "~", False: ""}[hemi],
    )
    df = df.query(query)
    all_stats = {}
    for (name, area) in atlas_glasser.areas.items():
        task = contrast_tfr.get_tfr(df.query('cluster=="%s"' % area), time_cutoff)
        all_stats.update(contrast_tfr.par_stats(*task, n_jobs=1))
    return all_stats
