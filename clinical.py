"""Code for processing clinical data """

"""
- extract labs
- relative and abs time stamp (careful with origin)
- limit time range (eg to numerics)
- plot labs
- lookup by LOINC
- allow for list of lab dataset names ['labs', 'laboratory']
- examples in specifications


- demographics
- example of search across files
- diagnosis lookup


"""
import h5py
import os.path
import pandas as pd
import json
from typing import Union
from ccdef import __DEBUG__, __VERSION__

def get_lab_dset (source: Union[h5py.File, str]):
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
    
    # TODO: allow capitalization or lowercase
    if 'clinical' in f.keys():
        if 'labs' in f['/clinical'].keys():
            lab_dset = f['/clinical/labs']
            return lab_dset
        else:
            raise Exception('No lab dataset located')
    else:
        raise Exception('No clinical group located')


def extract_labs (source: Union[h5py.File, str]):
    """
    Input: an HDF5 file handle or filename:

    - Read lab data from /clinical/labs dataset
    - Read test information from the dataset attribute .test_info
    
        .test_info is a JSON formatted list in the format:
        {'test_id': { 'label' : test label (str),
                    'category': test category (eg Blood gas, chemistry, etc) (str),
                    'fluid' : sample fluid (eg blood, urine, CSF) (str),
                    'valueuom': units of measurement for the test (str),
                    'loinc_code': LOINC (str)
                    }
        }


    return: timestamped labs as a pandas DataFrame
    """
    lab_dset = get_lab_dset(source)
    d=json.loads(lab_dset.attrs['.test_info'])

    # merge the labs with metadata to give a readable table
    items_df=pd.DataFrame.from_dict(d,orient='columns').T
    # typecast the testid to int in order to merge the dataframes
    items_df['testid']=items_df.index.astype(int)

    #get labs as a DataFrame
    labs = pd.DataFrame(lab_dset[:])

    readable_labs = pd.merge(labs,items_df, on = 'testid')[['time','label','value','valuenum','valueuom','flag',
                                                       'category','fluid','loinc_code']]

    #TODO: convert time to absolute (or relative?)
    return readable_labs.sort_values(by='time')

def lab_lookup ():    

    pass

    return 


