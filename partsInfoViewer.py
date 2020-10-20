# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 14:22:05 2020

@author: sebastian.chirinos
"""

import pickle

partsInfo = pickle.load( open( 'partsInfo.p', "rb" ),encoding='latin1')
print(partsInfo)