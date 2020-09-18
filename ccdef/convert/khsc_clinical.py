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


