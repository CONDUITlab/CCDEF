#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions for building and reading standardized signal names in ccdef files

given a file, identify datasets in numerics and waveforms
for each dataset, identify columns and mappings
add to mapping table

"""
import pandas as pd
import h5py
import numpy as np
import audata
#from ccdef._utils import df_to_sarray

std_signals = []

"""
dt = h5py.special_dtype(vlen=str)
comp_type = np.dtype([('parameter', dt), ('loinc', dt), ('source_name', dt), 
                      ('dataset', dt), ('column', 'i8')])
"""

""" Helper functions """

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

""" Reading functions """

def numerics (names = '', loincs = '', time = 'relative'):
    
    #read mapping df
    #make this a method of a mapping class?
    #map_df = pd.DataFrame(f.hdf['Mapping'][:])
    
    
    signals = []
    signal_names = []
    for name in names:
        local_name = map_df[map_df['parameter']==name]['local_name'].values[0]
        print ('{} maps to {}'.format(name, local_name))
        df=dset[local_name]
        signal_names.append(name)
        signals.append(df)
    output = pd.concat(signals,ignore_index=True, axis=1)
    output.columns=signal_names
    return

def waveforms (name = '', loinc='', time='relative'):
    
    return


    """Waveforms"""
    return

""" Writing/Encoding Functions """


def build_col_dict(dset, category, params):
    """generate mapping entries for a given dataset """

    col_dict = dset.columns 
    columns = {}
    counter = 0
    for idx, k in enumerate(col_dict.keys()):
        print (k)
        col_meta = {}
        ''' only interested in the key parameters '''
#        if k in params:
        if k is not None:
            counter += 1 
            col_meta['parameter'] = k # this will come from a lookup/reverse lookup from Loinc
            col_meta['dataset'] = dset.name
            col_meta['local_name']= k
            col_meta['column'] = idx+1
            col_meta['category'] = category
            col_meta['loinc'] = col_dict[k]['LOINC']
            columns[counter] = col_meta
            
    return columns

def make_mapping (filename):

    # open the file
    f = audata.File.open(filename, readonly=False)
    
    #get the numerics
    #for each dataset, get the columns
    #convert to dict
    #convert to df
    #append to dataset
    #save as dataset
    """Numerics"""
    signals = []

    for dset_name in f['Numerics'].list()['datasets']:
        dset = f['Numerics/'+dset_name]
        columns = build_col_dict(dset, 'Numerics', std_signals)
        df=pd.DataFrame.from_dict(columns, orient='index')
        signals.append(df)
    """Waveforms - if present"""
    
    for dset_name in f['Waveforms'].list()['datasets']:
        dset = f['Waveforms/'+dset_name]
        columns = build_col_dict(dset, 'Waveforms', std_signals)
        df=pd.DataFrame.from_dict(columns, orient='index')
        signals.append(df)
    
    
    """write to file"""
    
    """ test for existance of mapping table first - option to overwrite  """ 
    signals = pd.concat(signals)
    sarray, saType =  df_to_sarray(signals)
    f.hdf.create_dataset('Mapping', data=sarray, dtype=saType)
    f.close()
    
    
    
            
