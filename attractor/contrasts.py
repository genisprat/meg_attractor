import os
import pandas as pd
from attractor import utils, meta_data
from pymeg.contrast_tfr import Cache, compute_contrast, augment_data, logging


logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


from joblib import Memory

memory = Memory(location=os.environ["PYMEG_CACHE_DIR"], verbose=0)


contrasts = {
    "all": (["all"], [1]),
    "choice": (["hit", "fa", "miss", "cr"], (1, 1, -1, -1)),
    "stimulus": (["hit", "fa", "miss", "cr"], (1, -1, 1, -1)),
    "hand": (["left", "right"], (1, -1)),
}


def submit_contrasts(collect=False):
    import numpy as np
    import time

    tasks = []
    subjects = [1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14]
    for subject in subjects:
        for epoch in ['response']:
            tasks.append((contrasts, subject, epoch))
    res = []
    for cnt, task in enumerate(tasks):
        try:
            r = _eval(
                get_contrasts,
                task,
                collect=collect,
                walltime="02:30:00",
                tasks=6,
                memory=70,
            )
            res.append(r)
        except RuntimeError:
            print("Task", task, " not available yet")
    return res


@memory.cache()
def get_contrasts(
    contrasts, subject, epoch="stimulus", baseline_per_condition=False
):

    # Load meta!
    meta = meta_data.load_meta_data(subject)
    new_contrasts = {}
    for key, value in contrasts.items():
        new_contrasts[key + "lat"] = [value[0], value[1], "lh_is_ipsi"]
        new_contrasts[key + "avg"] = [value[0], value[1], "avg"]
    contrasts = new_contrasts

    files = {
        "stimulus": utils.get_filenames(subject, epoch="stimulus")[1],
        "response": utils.get_filenames(subject, epoch="response")[1],
        "baseline": utils.get_filenames(subject, epoch="stimulus")[1],
    }

    response_left = meta.choice == -1
    left_correct = meta.stim_sign == -1  #!TODO!
    meta = augment_data(meta, response_left, left_correct)

    cps = []
    with Cache() as cache:
        try:
            contrast = compute_contrast(
                contrasts,
                files[epoch],
                files["baseline"],
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


def _eval(func, args, collect=False, **kw):
    """
    Intermediate helper to toggle cluster vs non cluster
    """
    from pymeg import parallel

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


def rename(df):
    return df.rename(
        index={
            "alllat": "all",
            "allavg": "all",
            "handlat": "hand",
            "handavg": "hand",
            "choicelat": "choice",
            "choiceavg": "choice",
            "stimuluslat": "stimulus",
            "stimulusavg": "stimulus",
            "lh_is_ipsi": "lateralized",
            "avg": "average",
        }
    )


def plot(df, contrast="hand", hemi="lateralized"):
    from pymeg import contrast_tfr_plots as ctp

    c = ctp.PlotConfig(
        {"stimulus": (-0.35, 3.25), "response": (-1, 0.21)},  # Time windows for epochs
        ["all", "choice", "hand", "stimulus"],  # Contrast names
        stat_windows={"stimulus": (-0.5, 3.25), "response": (-1, 0.5)},
    )

    c.configure_epoch(
        "stimulus",
        **{
            "xticks": [0, 1, 2, 2.5],
            "xticklabels": ["0", "1"],
            "yticks": [25, 50, 75, 100],
            "yticklabels": [25, 50, 75, 100],
            "xlabel": "time",
            "ylabel": "Freq",
        },
    )

    c.configure_epoch(
        "response",
        **{
            "xticks": [0],
            "xticklabels": ["0", "1"],
            "yticks": [25, 50, 75, 100],
            "yticklabels": [25, 50, 75, 100],
            "xlabel": "time",
            "ylabel": "Freq",
        },
    )

    for key, values in {
        "choice": {"vmin": -25, "vmax": 25},
        "confidence": {"vmin": -25, "vmax": 25},
        "confidence_asym": {"vmin": -25, "vmax": 25},
        "hand": {"vmin": -25, "vmax": 25},
        "stimulus": {"vmin": -25, "vmax": 25},
    }.items():
        c.configure_contrast(key, **values)

    _ = ctp.plot_streams_fig(
        df.query('contrast=="%s" & hemi=="%s"' % (contrast, hemi)), contrast, c
    )
