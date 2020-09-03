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
import numpy as np
import h5py


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

def df_to_sarray(df):
    """
    Convert a pandas DataFrame object to a numpy structured array.
    Also, for every column of a str type, convert it into 
    a 'bytes' str literal of length = max(len(col)).

    :param df: the data frame to convert
    :return: a numpy structured array representation of df
    """
    dt = h5py.special_dtype(vlen=str)
    def make_col_type(col_type, col):
        try:
            if 'numpy.object_' in str(col_type.type):
                maxlens = col.dropna().str.len()
                if maxlens.any():
                    maxlen = maxlens.max().astype(int) 
                    col_type = dt
                else:
                    col_type = 'f2'
            return col.name, col_type
        except:
            print(col.name, col_type, col_type.type, type(col))
            raise

    v = df.values            
    types = df.dtypes
    numpy_struct_types = [make_col_type(types[col], df.loc[:, col]) for col in df.columns]
    dtype = np.dtype(numpy_struct_types)
    z = np.zeros(v.shape[0], dtype)
    for (i, k) in enumerate(z.dtype.names):
        # This is in case you have problems with the encoding, remove the if branch if not
        try:
            if dtype[i].str.startswith('|S'):
                z[k] = df[k].str.encode('latin').astype('S')
            else:
                z[k] = v[:, i]
        except:
            print(k, v[:, i])
            raise

    return z, dtype