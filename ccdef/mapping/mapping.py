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
import os.path
import audata
from tabulate import tabulate
from typing import Union
from ccdef._utils import df_to_sarray
from ccdef.mapping.loinc import LoincMapper
from ccdef import __DEBUG__, __VERSION__


std_signals = ['HR', 'ABP-S', 'ABP-M', 'ABP-D', 'NIBP-S', 'NIBP-M', 'NIBP-D', 'CVP', 'RR', 'SPO2',
               'ABP', 'PLETH', 'ECG-I','ECG-II','ECG-II','ECG-III','ECG-V']

"""
dt = h5py.special_dtype(vlen=str)
comp_type = np.dtype([('parameter', dt), ('loinc', dt), ('source_name', dt), 
                      ('dataset', dt), ('column', 'i8')])
"""


#%% reading functions
'''
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
'''
#%% Writing/Encoding Functions


def build_col_dict(dset, category, params, mapper):
    """generate mapping entries for a given dataset """

    col_dict = dset.columns 
    columns = {}
    counter = 0
    for idx, k in enumerate(col_dict.keys()):
        print (k)
        col_meta = {}
        ''' only interested in the key parameters '''
        ccdef_signal = mapper.local_label(k).ccdef
        if ccdef_signal in params:

            counter += 1 
            col_meta['signal'] = ccdef_signal 
            col_meta['dataset'] = dset.name
            col_meta['local_name']= k
            col_meta['column'] = idx+1
            col_meta['category'] = category
            col_meta['loinc'] = col_dict[k]['LOINC']
            col_meta['loinc_name'] = mapper.local_label(k).loinc_sn
            columns[counter] = col_meta
            
    return columns

def make_mapping (filename, mapper=None, overwrite=True):

    if mapper is None:
        mapper = LoincMapper(external_mapping_table="MIMICIII")
        
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

    for dset_name in f['numerics'].list()['datasets']:
        dset = f['numerics/'+dset_name]
        columns = build_col_dict(dset, 'numerics', std_signals, mapper)
        df=pd.DataFrame.from_dict(columns, orient='index')
        signals.append(df)
    """Waveforms - if present"""
    
    for dset_name in f['waveforms'].list()['datasets']:
        dset = f['waveforms/'+dset_name]
        columns = build_col_dict(dset, 'waveforms', std_signals, mapper)
        df=pd.DataFrame.from_dict(columns, orient='index')
        signals.append(df)
    
    
    """write to file"""
    
    """ test for existance of mapping table first - option to overwrite  """ 
    signals = pd.concat(signals)
    sarray, saType =  df_to_sarray(signals)
    # test for existance
    if 'mapping' in f['/'].list()['datasets']:
        print('Mapping table exists')
        if overwrite:
            del f.hdf['mapping']
            f.hdf.create_dataset('mapping', data=sarray, dtype=saType)
        else:
            print('Not overwritten')
    else:
        f.hdf.create_dataset('mapping', data=sarray, dtype=saType)
            
    f.close()
    
    
#show map

def show_mapping (source: Union[h5py.File, str]):
    if isinstance(source, h5py.File):
        if __DEBUG__:
            print('H5 file type supplied')
        f = source
        # test for existance of map
            
    elif isinstance(source, str):
        if __DEBUG__:
            print('Filename supplied')
        if not os.path.exists(source):
            raise Exception(f'File not found: {source}')
        else:
            f = h5py.File(source, 'r')
    
    if 'mapping' in f.keys():
        mapping = pd.DataFrame(f['mapping'][:])
    else:
        raise Exception('No mapping dataset located')
    
    print(tabulate(mapping,headers='keys', tablefmt='psql', showindex=False))

    return mapping

#use map

            
