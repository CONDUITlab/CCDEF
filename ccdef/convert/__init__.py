""" Conversion modules to create HDF5 files in the CCDEF format
- wfdb for converting physionet files
- xml to convert processed bedmaster files
- stp to convert raw bedmaster files (requires binary stptoxml)
-- clinical modules
      mimic3  extracts data from MIMIC 3 relational database and merges with ccdef waveform/numeric data files
      khsc    converts csv lab data from KHSC PCS and adds it to ccdef waveform/numeric data files
"""

__VERSION = 0.5
__DEBUG = False

