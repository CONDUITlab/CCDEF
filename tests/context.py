"""
ccdef package tests

"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import ccdef

print ('CCDEF Version: {}'.format(ccdef.__VERSION__))
#print (os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#print (sys.path)

