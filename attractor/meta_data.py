import numpy as np
import scipy.io as sio
import pickle
import os
import glob
import pandas as pd
from attractor import utils

def hash4(x):
    x.append(0)  # last 0 means no repetiotion
    x2 = tuple(x)
    if len(cache) == 0:
        sub = int(x[0])
        x_num = sub * 10000
        cache[x2] = x_num
        return x_num, 0
    try:
        x_num = max(cache.values()) + 1
        x[-1] = x[-1] + 1  # if it already exist then I add a 1 at the end.
        x2 = tuple(x)
        cache[x2] = x_num
        return x_num, 1
    except KeyError:
        x_num = max(cache.values()) + 1
        cache[x2] = x_num

        return cache[x2], 0


def load_meta_data(subject):
    def find_isigma(sigma_values, sigma):

        control = True
        isigma = 0
        while control:
            if np.abs(sigma - sigma_values[isigma]) < 0.01:
                control = False
            else:
                isigma = isigma + 1
        return isigma

    # path='/storage/genis/att_behavioral_data/data_S'+str(subject)
    # path='/archive/genis/Master_project/att_behavioral_data/data_S'+str(subject)
    path = "/storage/genis/att_behavioral_data/data_S" + str(subject)

    sigma0 = 0.02
    sigmaf = 1.0
    sigma_factor = (sigmaf / sigma0) ** (1.0 / 4.0)

    N_sigmas = 6
    sigma_values = []
    sigma_values.append(0)
    sigma_values.append(sigma0)
    for i in range(N_sigmas - 2):
        sigma_values.append(sigma_factor * sigma_values[-1])

    sigmas = []
    correct = []
    stim = []
    correct_side = []
    stim_sign = []
    mu = []
    conf_int = []
    S_duration = []
    choice = []
    i_sigmas = []
    date = []
    choice_rt = []
    block_number = []
    session_number = []
    trial_number = []
    for filename in glob.glob(os.path.join(path, "*Exp*SS*.mat")):
        print(filename)
        mat_contents = sio.loadmat(filename)
        # S_duration.append(mat_contents['t_sesion'][0][0])
        if (len(mat_contents["results"][0]) > 3):  ##alguns cop el programa falla i l'he de para abans.
            for i in range(len(mat_contents["results"][0]["sigma"])):
                # if not np.isnan(mat_contents['results'][0]['correct'][i][0][0]):
                sigmas.append(mat_contents["results"][0]["sigma"][i][0][0])
                i_sigmas.append(find_isigma(sigma_values, sigmas[-1]))
                correct.append(mat_contents["results"][0]["correct"][i][0][0])
                stim.append(mat_contents["results"][0]["xpositions"][i])
                mu.append(mat_contents["results"][0]["mu"][i][0][0])
                choice_rt.append(mat_contents["results"][0]["choice_rt"][i][0][0])
                date.append(mat_contents["results"][0]["session"][0][0][0:8])
                block_number.append(mat_contents["results"][0]["block_num"][i][0][0])
                session_number.append(
                    mat_contents["results"][0]["session_num"][i][0][0]
                )
                trial_number.append(mat_contents["results"][0]["trial"][i][0][0])
                stim_sign.append(mat_contents["results"][0]["side"][i][0][0])

                # if mat_contents["results"][0]["side"][i][0][0] == 1:
                #     stim_sign.append(1)
                #     if correct[-1]:
                #         choice.append(1)
                #     else:
                #         choice.append(-1)
                # else:
                #     stim_sign.append(-1)
                #     if correct[-1]:
                #         choice.append(-1)
                #     else:
                #         choice.append(1)
                        # hash_number.append(hash4([subject, int(session_number[-1]),int(block_number[-1]),int(trial_number[-1]),int(date[-1])]))


    choice=(2*np.array(correct)-1)*np.array(stim_sign)
    print(np.unique(stim_sign))
    print(np.unique(correct))
    print(np.unique(choice))
    data = {}
    data["correct"] = correct
    data["stim"] = stim
    data["mu"] = mu
    data["stim_sign"] = stim_sign
    data["sigmas"] = sigmas
    data["choice"] = list( choice )
    data["i_sigmas"] = i_sigmas
    data["block_num"] = block_number
    data["session_num"] = session_number
    data["trial_num"] = trial_number
    data["hash"]=[0]*len(trial_number)
    data["choice_rt"]=choice_rt
    meta_b = pd.DataFrame(data)
    
    meta_meg=utils.get_meta(subject)


    meta_meg.columns = ['baseline_start', 'decision_start', 'dot_onset', 'feedback', 'noise','choice', 'rest_delay', 'trial_end', 'trial_num', 'trial_start','wait_fix', 'session_num', 'block_num', 'first_dot', 'hash']


    meta_meg = meta_meg.set_index(['session_num', 'block_num', 'trial_num'])
    meta_b=meta_b.set_index(['session_num', 'block_num', 'trial_num'])



    meta_b2=meta_b.loc[meta_meg.index]
    meta_b2['hash']=meta_meg['hash']
    meta_b2['meg_choice']=meta_meg['choice']

    meta_b2=meta_b2.loc[meta_meg.index].dropna(subset=['choice','choice_rt'])
    #index_bad=meta_b[meta_b,'choice']==

    assert(all( meta_b2.loc[:,'choice']==meta_b2.loc[:,'meg_choice']))


    ### Now I addd the hash##############
    # meg_sessions=[5,6,7]

    # for session in groupby(meg_sessions:
    #     df_s=df[df.sesion_num==session]
    #     for block in df_s.block_num.unique()
    #         df_b=df_s[df_s.block_num==block]


    return meta_b2
