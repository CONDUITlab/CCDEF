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
from lxml import etree

#%% helper functions

def get_file_info (filename):
""" get start and end time from a bedmaster xml file """

_, elem = next(etree.iterparse(infile, tag='VitalSigns', 
   huge_tree=True, recover=True))
start_str = elem.attrib['CollectionTime']

start = pd.to_datetime(start_str, infer_datetime_format=True)

for _, element in etree.iterparse(infile, tag='VitalSigns',
    huge_tree=True, recover=True):
    time = element.attrib['CollectionTime']
    element.clear(keep_tail=True)
end_str = time
end = pd.to_datetime(end_str, infer_datetime_format=True)
duration = end-start

""" Examine the file header """
_, elem = next(etree.iterparse(infile, tag='FileInfo'))
bed = elem.findtext('Bed')
monitor_type = elem.findtext('FamilyType')

print('File runs {} to {}, duration is '.format(start, end, duration))

    return [start, end, duration, bed, monitor_type] 


#%% xml conversion
def convert_xml(infile, outfile, numerics=True, Waveforms=True):
    print('Converting {} to {}'.format(infile, outfile))

    for _, element in etree.iterparse(infile, events=("start", "end"), tag='VitalSigns',
        huge_tree=True, recover=True)):
        element.findtext('Time')
        vitals = element.getchildren()
        for i in vitals:
            time = i.findtext('Time')
            chan = i.findtext('Parameter')
            value = i.findtext('Value')
            uom = i.findtext('UOM')
            print(time, chan, value)
        element.clear(keep_tail=True)


#when creating new dataset, use total duration, sample rate, number of samples, to create dset
# overwrite in chunks as the data are read
# assign metadata at time of creation
# sample rate, col name, LOINC, basetime, scale
# look at audata Dataset creation - may be an issue with req col
#%% main

def main():

    infile = '/Volumes/ExternalPL/Data/KHSC/xml/new/K2ICU_BED05-1577888092.xml'
    outfile = '/Volumes/ExternalPL/Data/KHSC/test.h5'
    convert_xml(infile, outfile)
    return

if __name__ == "__main__":

    main ()