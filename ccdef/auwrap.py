import pandas as pd
import numpy as np
import h5py as h5
from typing import Optional, Union
import datetime as dt
from audata.file import File as AuFile

"""
Wrapper for the audata File class
"""


class File (AuFile):
    def __init__ (self,
                 file: h5.File,
                 time_reference: Optional[dt.datetime] = None,
                 return_datetimes: bool = True):
        super().__init__(file)
    
    def numerics(self, loinc=[], signals=[], time='relative'):
        print('Show numerics for {}'.format(loinc))
    
    def waveforms(self, loinc=[], signals=[], time='relative'):
        pass
        
    def show_map(self):
        print(pd.DataFrame(self['Mapping'].hdf[:]))