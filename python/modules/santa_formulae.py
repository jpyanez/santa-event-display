from . import *
from .function_wrapper import *

# Formulas for SANTA
def mc_tgamma( z, uz, zc, dc, tc, tini, c, n_index):
    """ Time of arrival of photons emitted by a track. """
    value = (tc-tini) + ((z-zc)*uz+(n_index**2 - 1)*mc_dgamma(z, uz, zc, dc, c, n_index)/n_index)/c
    return value

def mc_dgamma( z, uz, zc, dc, c, n_index):
    """ Distance traveled by a photon between track and sensor. """
    value = (n_index/sqrt(n_index**2 - 1))*sqrt(dc**2 + ((z-zc)**2)*(1-uz**2))
    return value

def mc_tgamma_bp(z, zc, dc, tini, c, n_index):
    """ Time of arrival of photons emitted by a point source. """
    value = tini + n_index * mc_dgamma_bp(z, zc, dc)/c
    return value

def mc_dgamma_bp(z, zc, dc):
    """ Distance traveled by a photon between point and sensor. """
    value = sqrt(dc**2 + (z - zc)**2)
    return value

def paramsFromTrack(string_xy, track):
    """ Converts track parameters into SANTA parameters """

    if type(track) == santa_type:
        print('SANTA/BBFit style track ', track)
        params = dummyClass( zc = santa_zc(track), dc = santa_dc(track), 
                             tc = santa_tc(track), uz = santa_uz(track))
        return params


    tini = track.time
    c = dataclasses.I3Constants.c
    n = n_detector_specific  

    qx = particle_x(track)
    qy = particle_y(track)
    qz = particle_z(track)

    new_theta = particle_zenith(track) - pi/2
    new_phi = mod((particle_azimuth(track) + pi), 2*pi)
    ux = cos(new_theta)*cos(new_phi)
    uy = cos(new_theta)*sin(new_phi)

    uz = sin(new_theta)
    zc = (qz - uz*(qx*ux + qy*uy + qz*uz) + uz*(string_xy[0]*ux + string_xy[1]*uy))/(1-uz**2)
    tc =  tini + (string_xy[0]*ux + string_xy[1]*uy + qz*uz - (qx*ux + qy*uy + qz*uz))/(c*(1-uz**2))
    #tc =  tini + (string_xy[0]*ux + string_xy[1]*uy + zc*uz - (qx*ux + qy*uy + qz*uz))
    dc = sqrt((qx+c*ux*(tc - tini)-string_xy[0])**2 + (qy+c*uy*(tc - tini)-string_xy[1])**2)
    
    # Parameters for a track
    params = dummyClass( zc = zc, dc = dc, tc = tc, uz = uz)
    #print 'SANTA-display: parameters (zc,dc,tc,uz): ', params.zc, params.dc, params.tc, params.uz

    return params


