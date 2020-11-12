"""
khsc_clinical.py

Functions for converting KHSC clinical date (lab, micro) to CCDEF format.
For details of ccdef, see www.ccdef.org

This module assumes that the following files are available (as csv):

    - labs
    - moves
    - admits

And that the files have been anonymized so that they are indexed by Subj_id and Visit_id
"""

from ccdef._utils import df_to_sarray
import pandas as pd

path = '/mnt/data04/Conduit/pcsdata/latest/'

""" TODO:

- given xml/hd5 file:
    - match to subject
- extract data for a given subject
- write to file
- create dataset metadata

"""

"""
   ldf=ldf.reset_index()
    for idx, row in ldf.iterrows():
        ldf['Time'].iloc[idx]=((base_datetime-pd.to_datetime(row['Order_datetime'])).total_seconds())
"""

"""
fs = fold['/Numerics/Vitals'].attrs['sample_rate']
origin = pd.to_datetime(fold['/Numerics/Vitals'].attrs['base_datetime'])
filemeta = {'ccdef version' : 1.0, 'source':'Conduit Labs/KHSC'}
fnew = audata.File.new('KHSC.h5', time_reference=origin, metadata = filemeta, overwrite=True)
fnew.hdf['/'].attrs['.demographics'] = json.dumps({'age':67, 'gender':'M'})
vitals = list(fold['/Numerics/Vitals'].keys())
for name in vitals:
    dset_name = '/Numerics/Vitals/'+name
    dset = fold[dset_name]
    end = len(dset)
    ts = make_ts(end, fs, time_type=abs, origin=origin)
    df = pd.DataFrame(data=dset[:],columns=[name])
    df.insert(loc=0, column='time', value=ts)
    fnew['/numerics/'+name] = df

wfs = list(fold['/Waveforms/Hemodynamics/'].keys())
fs = fold['/Waveforms/Hemodynamics'].attrs['sample_rate']
origin = pd.to_datetime(fold['/Waveforms/Hemodynamics'].attrs['base_datetime'])

for name in wfs:
    if name in ['PA2', 'V']:
        continue
    dset_name = '/Waveforms/Hemodynamics/'+name
    dset = fold[dset_name]
    end = len(dset)
    ts = make_ts(end, fs, time_type=abs, origin=origin)
    df = pd.DataFrame(data=dset[:],columns=[name])
    df.insert(loc=0, column='time', value=ts)
    fnew['/waveforms/'+name] = df


fnew.close()
# add metadata

"""