from . import icecube_icetray, km3net_seatray
from . import dataclasses, simclasses, icetray

if icecube_icetray:
    try:
        from icecube import santa
        santa_type = santa.I3SantaFitParams
    except:
        santa_type = None
        print('SANTA-display: No SANTA libraries')
elif km3net_seatray:
    from . import antares_common
    santa_type = santa.I3BBFitRecoParams

#####
## Defining the single string fit type
#####


def santa_uz(fit):
    if icecube_icetray:    return fit.uz
    if km3net_seatray:     return fit.SingleStringTrackCosZenith

def santa_zc(fit):
    if icecube_icetray:    return fit.zc
    if km3net_seatray:     return fit.SingleStringTrack_z0

def santa_dc(fit):
    if icecube_icetray:    return fit.dc
    if km3net_seatray:     return fit.SingleStringTrack_d0

def santa_tc(fit):
    if icecube_icetray:    return fit.tc
    if km3net_seatray:     return fit.SingleStringTrack_t0

#####
## I3Particles and AnataresRecoParticles
#####

def particle_x(particle):
    if icecube_icetray:    return particle.pos.x
    if km3net_seatray:     return particle.x

def particle_y(particle):
    if icecube_icetray:    return particle.pos.y
    if km3net_seatray:     return particle.y

def particle_z(particle):
    if icecube_icetray:    return particle.pos.z
    if km3net_seatray:     return particle.z

def particle_zenith(particle):
    if icecube_icetray:    return particle.dir.zenith
    if km3net_seatray:     return particle.zenith


def particle_azimuth(particle):
    if icecube_icetray:    return particle.dir.azimuth
    if km3net_seatray:     return particle.azimuth

#####
## Geometry
#####
def dom_x(geometry, omkey):
    #print(omkey)
    if icecube_icetray: return geometry.omgeo[omkey].position.x
    if km3net_seatray:  return geometry.omgeo[omkey].position.X

def dom_y(geometry, omkey):
    if icecube_icetray: return geometry.omgeo[omkey].position.y
    if km3net_seatray:  return geometry.omgeo[omkey].position.Y

def dom_z(geometry, omkey):
    if icecube_icetray: return geometry.omgeo[omkey].position.z
    if km3net_seatray:  return geometry.omgeo[omkey].position.Z

#####
## Pulses
#####
def read_pulses(frame, series_name):
    try:
        # For masks-ready icetray
        dataclasses.I3RecoPulseSeriesMapMask
        if type(frame[series_name]) == dataclasses.I3RecoPulseSeriesMapMask:
            hit_map = frame[series_name].apply(frame)
        else:
            hit_map      = frame[series_name]
    except:
        # Older versions (including Km3net_Seatray's version)
        hit_map      = frame[series_name]
    return hit_map

def pulse_charge(pulse):
    if icecube_icetray: return pulse.charge
    if km3net_seatray:  return pulse.Charge

def pulse_time(pulse):
    if icecube_icetray: return pulse.time
    if km3net_seatray:  return pulse.Time
