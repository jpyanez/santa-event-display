from . import dataclasses, simclasses
from . import array, OrderedDict

## Pulses
pulseType = [dataclasses.I3RecoPulseSeriesMap, 
             dataclasses.I3RecoPulseSeriesMapMask,
             dataclasses.I3DOMLaunchSeriesMap,
             dataclasses.I3MCHitSeriesMap]

selectedPulses = ['OfflinePulses',
                  'InIce',
                  'Upgrade',
                  'SANTA',
                  'TWSRT', 
                  'SRTTW', 
                  'MCHit']

## Particles
try:
    from icecube import santa
    particleType = [dataclasses.I3Particle,
                        santa.I3SantaFitParams]#, # Expand it before?
                        #dataclasses.I3MMCTrackList] # Expand it before
except:
        particleType = [dataclasses.I3Particle]
        print('SANTA-display: No SANTA libraries')


selectedParticles = ['MCMostEcascade',
                     'MCMostEtrack',
                     'MMCTrackList', 
                     'LineFit' , 
                     'SANTA' , 
                     'SPE']

## Layout selector items
figureLayouts = OrderedDict([ ('Upgrade IL', 
                               array([[86,0,81,0,82],[0,0,36,92,0],[0,87,88,91,83],
                                      [85,89,79,90,80],[0,0,84,0,0]])),
                              ('DeepCore IL', 
                               array([[0,0,81,0,0],[86,0,0,0,82],[0,0,36,0,0],
                                      [85,79,0,80,83],[0,0,84,0,0]])), 
                              ('DeepCore IIL', 
                               array([[0,0,45,0,46,0,0],[0,0,0,81,0,0,0],[0,86,0,0,0,82,0],
                                      [35,0,0,36,0,0,37],[0,85,79,0,80,83,0],[0,0,0,84,0,0,0],
                                      [0,26,0,0,0,27,0]])),
                              ('IC86 L',
                               array([[0,0,0,0,0,75,0,76,0,77,0,78,0,0,0,0,0,0,0,0],
                                      [0,0,0,0,68,0,69,0,70,0,71,0,72,0,73,0,74,0,0,0],
                                      [0,0,0,60,0,61,0,62,0,63,0,64,0,65,0,66,0,67,0,0],
                                      [0,0,51,0,52,0,53,0,54,0,55,0,56,0,57,0,58,0,59,0],
                                      [0,41,0,42,0,43,0,44,0,45,0,46,0,47,0,48,0,49,0,50],
                                      [31,0,32,0,33,0,34,0,35,0,36,0,37,0,38,0,39,0,40,0],
                                      [0,22,0,23,0,24,0,25,0,26,0,27,0,28,0,29,0,30,0,0],
                                      [0,0,14,0,15,0,16,0,17,0,18,0,19,0,20,0,21,0,0,0],
                                      [0,0,0,7,0,8,0,9,0,10,0,11,0,12,0,13,0,0,0,0],
                                      [0,0,0,0,1,0,2,0,3,0,4,0,5,0,6,0,0,0,0,0]])),
                              ('DC+Upgrade',
                               array([79,80,81,82,83,84,85,86,
                                      87,88,89,90,91,92])),
                              ('DeepCore I',
                               array([36,79,80,81,82,83,84,85,86])), 
                              ('DeepCore II', 
                               array([26, 27, 37, 46, 45, 35, 36,79,
                                      80,81,82,83,84,85,86])),
                              ('Extended DC', 
                               array([25, 34, 44, 54, 47, 26, 27, 37, 46, 
                                      45, 35, 36,79,80,81,82,83,84,85,86])),
                              ('IC86',
                               array(range(1,87)))
                          ])

