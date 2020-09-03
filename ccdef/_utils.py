#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 21:40:29 2020

@author: Phil
"""


"""

hd5 helper functions

"""

import pandas as pd

def slice_hd5 (infile, outfile, start_time, duration):
    # get dataset names
    hdf = pd.HDFStore(infile)
    keys = hdf.keys()
    hdf.close()
    end_time = pd.to_datetime(start_time) + pd.to_timedelta(duration, 'S')    
    print ('File {} has the following datasets: {}'.format(infile, keys))
    for key in keys:
        # *may* need to modify this for large slices... read in chunks and loop
        df = pd.read_hdf(infile, key, where='index>start_time & index<end_time')
        df.to_hdf(outfile, key, append = True, format = 't')  
        
def hdf_stats (infile):
    hdf = pd.HDFStore(infile)
    keys = hdf.keys()
    hdf.close()
    for key in keys:
        print ('Dataset {}:'.format(key))
        key_start = pd.read_hdf(infile, key=key, start=0, stop=1).index[0]
        key_end = pd.read_hdf(infile, key=key, start=-1).index[0]
        duration = key_end-key_start
        print ('Starts at {:%Y-%m-%d %H:%M:%S}\nEnds at {:%Y-%m-%d %H:%M:%S}\nDuration: {}\n'.format(key_start, key_end, duration))
