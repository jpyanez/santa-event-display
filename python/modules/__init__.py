# __init__.py

# Global imports
from os.path import expanduser
from collections import OrderedDict
from sys import argv
from PyQt5 import QtCore, QtGui, QtWidgets
from numpy import sin, cos,  arange, pi, array, sqrt, reshape, ceil, append, where, median, mean, linspace, mod, unique, nan, log10, log, vstack, arcsin, isnan, zeros, argsort, delete
import numpy as np
from icecube import dataio, dataclasses, icetray, simclasses

from .usr_cfg import *


class dummyClass:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

# Km3Net vs IceCube (better way to do this?)
icecube_icetray = False
km3net_seatray  = False

try:
    from icecube import santa
    icecube_icetray = True
except:
    # Need to come up with a better way to decide on the experiment.
    # Quick and dirty for now
    icecube_icetray = True
    print('SANTA-display: No SANTA libraries loaded. The SANTA recos will not be available')
try:
    from icecube import antares_common
    from icecube import antares_bbfit_reco as santa
    km3net_seatray = True
    icecube_icetray = False
except:
    print('SANTA-display: No ANTARES libraries loaded.')

if icecube_icetray:
    #try:
        from .icecube_settings import *
        n_detector_specific = dataclasses.I3Constants.n_ice
    #except:
    #    print('IceCube user: settings could not be loaded!')
    #    exit()
elif km3net_seatray:
    try:
        from km3net_settings import *
        n_detector_specific = dataclasses.I3Constants.n_water_antares
    except:
        print('Km3NeT user: settings could not be loaded!')
        exit()
else:
    print('IceCube user: you need the santa module installed to be able to use this viewer')
    print('Km3NeT user: you need the antares_bbfit_reco module installed to be able to use this viewer')
    exit()



# antares_bbfit_reco.I3BBFitRecoParams.SingleStringBrightPoint_d0
# antares_bbfit_reco.I3BBFitRecoParams.SingleStringBrightPoint_t0
# antares_bbfit_reco.I3BBFitRecoParams.SingleStringBrightPoint_z0
# antares_bbfit_reco.I3BBFitRecoParams.SingleStringTrackCosZenith
# antares_bbfit_reco.I3BBFitRecoParams.SingleStringTrack_d0
# antares_bbfit_reco.I3BBFitRecoParams.SingleStringTrack_t0
# antares_bbfit_reco.I3BBFitRecoParams.SingleStringTrack_z0
# antares_bbfit_reco.FitResultType.BrightPoint
# antares_bbfit_reco.FitResultType.Track 
