#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 21:40:29 2020

@author: Phil
"""

import pandas as pd
import numpy as np
import json
import h5py
import os.path
from typing import Union
from ccdef import __DEBUG__, __VERSION__

#%% file helper functions

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

#%% Dataset helper functions

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
                    # maxlen = maxlens.max().astype(int) 
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
    
def traverse_datasets(hdf_group):
    def h5py_dataset_iterator(g, prefix=''):
        for key in g.keys():
            item = g[key]
            path = f'{prefix}/{key}'
            if isinstance(item, h5py.Dataset): # test for dataset
                yield (path, item)
            elif isinstance(item, h5py.Group): # test for group (go down)
                yield from h5py_dataset_iterator(item, path)

    for path, _ in h5py_dataset_iterator(hdf_group):
        yield path

def scan_file (source: Union[h5py.File, str], verbose=False):
    """
    Convert a pandas DataFrame object to a numpy structured array.
    Also, for every column of a str type, convert it into 
    a 'bytes' str literal of length = max(len(col)).

    :param filename: the file to scan
    :return: [top level groups, top level datasets]
    """
    # todo: test to see if file is hdf5
    if isinstance(source, h5py.File):
        if __DEBUG__:
            print('H5 file type supplied')
        f = source
            
    elif isinstance(source, str):
        if __DEBUG__:
            print('Filename supplied')
        if not os.path.exists(source):
            raise Exception(f'File not found: {source}')
        else:
            f = h5py.File(source, 'r')

    root = f['/']
    #get top level
    top_groups = []
    top_dsets = []
    for key in root.keys():
        if isinstance(f[key], h5py.Group):
            top_groups.append(f[key])
        if isinstance(f[key], h5py.Dataset):
            top_dsets.append(f[key])


    print ('Top level attributes and metadata:')        
    for key, val in root.attrs.items():
        print ("{} : {}".format(key, val))

    print('\nTop level groups')
    for g in top_groups:
        print (g.name)
#        g.visititems(iterate_group)

    print('\nTop level datasets')
    for dset in top_dsets:
        print (dset.name)
#        print(dset.dtype)
        dt = dset.dtype.fields
#        print(dt)
        if dt is not None:
            d = dict (dt)
            for key,value in d.items():
                print ('\t{} : {}'.format(key, str(value).split(("'"))[1]))
        else:
            print ('\tDtype: {}'.format(root[dset].dtype))


    print('\nRecursing top level groups')
    for g in top_groups:
        print('\nGroup: {}'.format(g.name))
        for dset in traverse_datasets(g):
            print ('\t{}'.format(dset))
            if verbose:
                dt = f[g.name+dset].dtype.fields
                if dt is not None:
                    d = dict (dt)
                    for key,value in d.items():
                        print ('\t\t{} : {}'.format(key, str(value).split(("'"))[1]))
                else:
                    print ('\t\tDtype: {}'.format(f[g.name+dset].dtype))

    tg_names = [x.name for x in top_groups]
    td_names = [x.name for x in top_dsets]
    
    if isinstance(source, h5py.File):
        f.close()
        
    return [tg_names, td_names]  


def _fix_meta(filename):
    """ Fix metadata formatting

    May need to use json.loads and json.dumps
    """

    f = h5py.File(filename,'r+')

    #move metadata from group to root attribute

    for item in list(f['/.meta'].attrs):
        f['/'].attrs[item] = f['/.meta'].attrs[item]

    #remove .meta group
    del f['.meta']


def make_ts_dset (dset, time_type = 'abs'):
    pass
    return

def make_ts_wfdb_rec (record, time_type = 'abs'):
    pass
    return


def make_ts (dset, time_type='abs'):
    """
    make a time series for dset using the sample rate and basetime/origin from the dataset metadata


    returns:
        TimeDeltaIndex if time_type is rel
        DateTimeIndex if time_type is abs

    """
    
    ds_meta = json.loads(dset.attrs['.meta'])
    key = list(ds_meta['columns'].keys())[0]
    meta_keys = ds_meta['columns'][key].keys()
    if 'base_datetime' in meta_keys:
        origin = pd.to_datetime(ds_meta['columns'][key]['base_datetime'])
    elif 'time_origin' in meta_keys:
        origin = pd.to_datetime(ds_meta['columns'][key]['time_origin'])
    else:
        raise Exception('No time origin located in dataset metadata')
        
    fs = ds_meta['columns'][key]['sample_rate']
    dt = round(1 / fs,6) # time step
    end = len(dset)
    
    if time_type == 'rel':
        ts = pd.TimedeltaIndex( np.arange (0, end*dt, dt ), unit = 's', name = 'Timedelta' )
        return origin, ts

    else:
        ts = (pd.TimedeltaIndex( np.arange (0, end*dt, dt ), unit = 's', 
            name = 'Datetime' ) + origin).tz_localize(tz='EST')
        return origin, ts