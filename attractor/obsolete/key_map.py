#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 12:01:36 2016

@author: crm
"""

import numpy as np
import cPickle
import os

mapname = 'key_map.pickle'

try:
  cache = cPickle.load(open(mapname))
except IOError:
  cache = {'start':0}


def hash(x):

    x = tuple(x)
    try:
        return cache[x]
    except KeyError:
        cache[x] = max(cache.values())+1
        cPickle.dump(cache, open(mapname, 'w'), protocol=2)
        return cache[x]

    