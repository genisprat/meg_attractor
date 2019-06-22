"""
Common helper functions to organize data.
"""
from pathlib import Path
import pandas as pd
preprocessed_path = Path('/storage/genis/preprocessed_megdata')


def get_filenames(subject, dtype='source', session='*', epoch='*'):
    if 'source' in dtype:
        path = preprocessed_path / 'source_space'
        globstr = 'S%i-SESS%s-*%s*lcmv.hdf'%(subject, str(session), str(epoch))                
    elif 'meta' in dtype:
        path = preprocessed_path / 'meta'
        globstr = 'down_sample_%s_meta_sub%i_sess%s_b*.hdf'%(epoch[:4], subject, str(session))        
    else:
        raise ValueError('dtype can only be "source" at the moment')
    return path.glob(globstr), str(path/globstr)

def get_meta(subject):
    files = list(get_filenames(subject, 'meta', epoch='stim')[0])
    print(files)
    return pd.concat([pd.read_hdf(x) for x in files])