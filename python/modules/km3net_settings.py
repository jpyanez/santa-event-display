from . import dataclasses, simclasses, antares_common
from . import array, OrderedDict

## Pulses
pulseType = [dataclasses.I3RecoPulseSeriesMap, 
             dataclasses.I3DOMLaunchSeriesMap,
             dataclasses.I3MCHitSeriesMap]

selectedPulses = ['MCHit',
                  'RecoPulse',
                  'BBFit'
                  ]

## Particles
particleType = [dataclasses.I3Particle,
                antares_common.AntaresRecoParticle]
                #santa.I3SantaFitParams

selectedParticles = ['MCMostEtrack',
                     'MCMostEcascade',
                     'BBFit']

## Layout selector items
figureLayouts = OrderedDict([('Km3NeT',
                              array(range(1,5)))
                         ])
