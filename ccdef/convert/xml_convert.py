#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert XML to ccdef

Created on Thu Jun  7 10:09:17 2018

7 Oct 2019:
    Updated to work with BedMaster stp ToolKit version 8.5

"""
import h5py
import audata
import mmap
import pandas as pd

#%% helper functions

def get_file_info (filename):
# get start and end time from a bedmaster xml file
    

    with open(filename, 'rb') as f:
        # memory-map the file, size 0 means whole file
        m = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)  
                              # prot argument is *nix only

        i = m.find(b'<Waveforms CollectionTime')   # search for last occurrence of 'word'
        m.seek(i)             # seek to the location
        line = m.read(85)
        start_str = str(line).split('CollectionTime="')[1].split('"')[0]
        start = pd.to_datetime(start_str, infer_datetime_format=True)

        i = m.rfind(b'<Waveforms CollectionTime')   # search for last occurrence of 'word'
        m.seek(i)             # seek to the location
        line = m.read(85)
        end_str = str(line).split('CollectionTime="')[1].split('"')[0]
        end = pd.to_datetime(end_str, infer_datetime_format=True)

        duration = end-start
    
    return [start, end, duration] 



#%% xml conversion

