"""HDF5 file wrapper class"""

import h5py

from ccdef import __VERSION__, __DEBUG__
from ccdef._utils import scan_file as file_info
from ccdef.mapping.mapping import show_mapping

class File():
    """ File wrapper
    
    
     """

    def __init__ (self, filename=None):
        if filename is not None:
            self.hdf = h5py.File(filename, 'r')
        
#    def open (self, filename:str):
#        self.hdf = h5py.File(filename, 'r')

    def file_info(self, verbose=True):
        file_info(self.hdf, verbose)
        
    def show_mapping(self):
        show_mapping(self.hdf)

    def close(self):

        """Close the file handle."""
        if self.hdf is not None:
            self.hdf.close()

    def flush(self):
        """Flush changes to disk."""
        if self.hdf is not None:
            self.hdf.flush()
        else:
            raise Exception('No file opened!')

    """
    def __repr__(self):
        return self.__getitem__('').__repr__()

    def __str__(self):
        return self.__getitem__('').__str__()
    """
    def __enter__(self):
        return self

    def __exit__(self, exit_type, value, traceback):
        self.close()
        
