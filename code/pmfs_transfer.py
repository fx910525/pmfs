#This module has the functions that calculate the transfer function, its derivatives, and the brightness-temperature fluctuations.

import numpy as np
import cosmo_functions as cf
reload(cf)
from constants import *
from globals import *
from geometric_functions import Y2
from numba import jit

@jit#(nopython=True)
def pattern_Tb(thetak=np.pi/3., phik=np.pi/8., thetan=np.pi/3., phin=np.pi/4., 
            xalpha=34.247221, xc=0.004176, xB=0.365092):
    
    """ 
    NOTE: Magnetic-field direction is along the z-axis!
    It takes x's (all unitless),
    and angles in [rad]."""
  
    summ = 0.
    for i,m in enumerate( np.array([-2,-1,0,1,2]) ):
        summand = Y2( m,thetak,phik ) * np.conjugate( Y2( m,thetan,phin ) ) / (1. + xalpha + xc - 1j*m*xB)
        summ += summand.real

    return summ
    

@jit#(nopython=True)
def calc_Tb(thetak=np.pi/3., phik=np.pi/8., thetan=np.pi/3., phin=np.pi/4., 
            delta=0., Ts=11.1, Tg=57.23508, z=20, verbose=False,
            xalpha=34.247221, xc=0.004176, xB=0.365092, x1s=1.):
    
    """ Calculates brightness-temperature fluctuation T[K] from eq 1 of Paper II. 
    NOTE: Magnetic-field direction is along the z-axis!  It takes x's (all unitless), temperatures in [K], and angles in [rad]."""
    
    k_dot_n = np.cos(thetan)*np.cos(thetak) + np.sin(thetan)*np.sin(thetak)*np.cos(phin)*np.cos(phik) + np.sin(thetan)*np.sin(thetak)*np.sin(phin)*np.sin(phik)

    summ = 0.
    for i,m in enumerate( np.array([-2,-1,0,1,2]) ):
        summand = Y2( m,thetak,phik ) * np.conjugate( Y2( m,thetan,phin ) ) / (1. + xalpha + xc - 1j*m*xB)
        summ += summand.real

    first_term = 1 + delta + delta*k_dot_n**2
    second_term = 1 + 2.*delta + 2.*delta*k_dot_n**2 - delta*4.*np.pi/75.*summ
    
    res = x1s * ( 1 - Tg/Ts ) * np.sqrt( (1 + z)/10. ) * ( 26.4 * first_term - 0.128 * x1s * ( Tg/Ts ) * np.sqrt( (1 + z)/10. ) * second_term)
    
    if verbose:
        print '\n'
        print 'xalpha = %f' % xalpha
        print 'xc = %f' % xc
        print 'xB = %f' % xB
        print 'k_dot_n=%f' % k_dot_n
        print 'summ=%f' % summ
        print 'first=%f' % 26.4*first_term
        print 'second=%f' % second_term
        
    return res/1000. #this is to make it to K from mK.



@jit#(nopython=True)    
def calc_deltaTb(thetak=np.pi/2., phik=0., thetan=np.pi/2., phin=np.pi/4., 
            delta=0., Ts=11.1, Tg=57.23508, z=20, verbose=False,
            xalpha=34.247221, xc=0.004176, xB=0.365092, x1s=1.):
    
    """ Calculates the fluctuations in brightness temperature T[K], with \delta=0 case subtracted. 
    NOTE: Magnetic-field direction is along the z-axis!  It takes x's (all unitless), temperatures in [K], and angles in [rad]."""
    
    res0 = calc_Tb(thetak=thetak, phik=phik, thetan=thetan, phin=phin, 
            delta=0., Ts=Ts, Tg=Tg, z=z, verbose=verbose,
            xalpha=xalpha, xc=xc, xB=xB)

    res = calc_Tb(thetak=thetak, phik=phik, thetan=thetan, phin=phin, 
            delta=delta, Ts=Ts, Tg=Tg, z=z, verbose=verbose,
            xalpha=xalpha, xc=xc, xB=xB)
    
    if verbose:
        print '\n\nTb(delta=0) = %f mK' % res0
        print 'Tb(delta) = %f mK' % res
        print 'Tb(delta) - Tb(delta=0) = %f mK' % ( res - res0 )
    return ( res - res0 )




@jit#(nopython=True)
def calc_G(thetak=np.pi/2., phik=0., thetan=np.pi/2., phin=np.pi/4., 
            Ts=11.1, Tg=57.23508, z=20, verbose=False,
            xalpha=34.247221, xc=0.004176, xB=0.365092, x1s=1.):
    
    """Calculates the transfer function, which is the total derivative dT/ddelta evaluated at delta=0, 
    from eq 24 of Paper II. Result is in [K]. It takes x's (all unitless), temperatures in [K], and angles in [rad].
    B is along z!"""
    
    k_dot_n = np.cos(thetan)*np.cos(thetak) + np.sin(thetan)*np.sin(thetak)*np.cos(phin)*np.cos(phik) + np.sin(thetan)*np.sin(thetak)*np.sin(phin)*np.sin(phik)
      
    summ = 0.
   
    #for i,m in enumerate( np.array([-2,-1,0,1,2]) ):#---->causes jit issues
    for m in [-2,-1,0,1,2]:
        summand = Y2( m,thetak,phik ) * np.conjugate( Y2( m,thetan,phin ) ) / ( 1. + xalpha + xc - 1j*m*xB )
        summ += summand.real
    #if np.isclose(summ, 0.):#---->causes jit issues
    #    summ = 0.#---->causes jit issues
    first_term = 1 + k_dot_n**2
    second_term = 2. + 2.*k_dot_n**2 - 4.*np.pi/75.*summ

    res = x1s * ( 1 - Tg/Ts ) * np.sqrt( (1 + z)/10. ) * ( 26.4 * first_term - 0.128 * x1s * (Tg/Ts) * np.sqrt( (1 + z)/10. ) * second_term)

    return res/1000. #this is to make it to K from mK.


@jit#(nopython=True)
def calc_dGdB(thetak=np.pi/2., phik=0., thetan=np.pi/2., phin=np.pi/4., 
            Ts=11.1, Tg=57.23508, z=20, verbose=False,
            xalpha=34.247221, xc=0.004176, xBcoeff=3.65092e18, x1s=1.,
            debug=False):

    """Calculates the derivative of the transfer function wrt the magnitude of a homogeneous component
    of the magnetic field B(z) *at a given redshift* ( such that B(z)=B0*(1+z)^2 ), evaluated at B=0, 
    from analytic derivative of eq 1 of Paper II. Result is in [K/Gauss].
    B is along z-axis.  It takes x's (all unitless), temperatures in [K], and angles in [rad]."""

    summ = 0.
    ####if np.isclose(thetan, np.pi/2.) and np.isclose(phin, 0.): #---->causes jit issues
    #if (thetan==np.pi/2.) and (phin==0.):
    #    summ = 0.25*(15./(2.*np.pi)) * np.sin(thetak)**2 * np.sin(2.*phik)
    #else:
    for i,m in enumerate( np.array([-2,-1,0,1,2]) ):
            summand =  1j * m * Y2( m,thetak,phik ) * np.conjugate( Y2(m,thetan,phin) ) 
            summ += summand.real

    #if np.isclose(summ, 0.):#---->causes jit issues
    #    summ = 0.#---->causes jit issues
    summ *= xBcoeff / ( 1. + xalpha + xc )**2
    
    res = (0.128*4.*np.pi/75.) * x1s**2 * ( 1 - Tg/Ts ) * (Tg/Ts) * (1 + z)/10. * summ
    if debug:
        xs = xBcoeff / ( 1. + xalpha + xc )**2
        return res/1000., summ, xs
    return res/1000. #this is to make it to K from mK.



@jit#(nopython=True)
def calc_G_Bzero(thetak=np.pi/2., phik=0., thetan=np.pi/2., phin=np.pi/4., 
            Ts=11.1, Tg=57.23508, z=20, verbose=False,
            xalpha=34.247221, xc=0.004176, x1s=1.):
    
    """
    NOT USED in fisher. 
    In the limit B->0 calculates the transfer function, which is the derivative dT/ddelta evaluated at delta=0, 
    of eq 1 of Paper II.
    Result is in [K]. It takes x's (all unitless), temperatures in [K], and angles in [rad].
    B is along z!"""
    
    k_dot_n = np.cos(thetan)*np.cos(thetak) + np.sin(thetan)*np.sin(thetak)*np.cos(phin)*np.cos(phik) + np.sin(thetan)*np.sin(thetak)*np.sin(phin)*np.sin(phik)


    summ = 0.5*(3.*k_dot_n**2 - 1.)/ ( 1. + xalpha + xc )
        
    first_term = 1 + k_dot_n**2
    second_term = 2. + 2.*k_dot_n**2 - 1./15.*summ

    res = x1s * ( 1 - Tg/Ts ) * np.sqrt( (1 + z)/10. ) * ( 26.4 * first_term - 0.128 * x1s * (Tg/Ts) * np.sqrt( (1 + z)/10. ) * second_term)

    return res/1000. #this is to make it to K from mK.


#@jit#(nopython=True)
def calc_G_Binfinity(thetak=np.pi/2., phik=0., thetan=np.pi/2., phin=np.pi/4., 
            Ts=11.1, Tg=57.23508, z=20, verbose=False,
            xalpha=34.247221, xc=0.004176, x1s=1.):
    
    """In the limit B->infinity calculates the transfer function, which is the total derivative dTb/ddelta evaluated at delta=0, 
    from analytic derivative of eq 1 of Paper II.
    Result is in [K]. It takes x's (all unitless), temperatures in [K], and angles in [rad].
    B is along z!"""
    
    k_dot_n = np.cos(thetan)*np.cos(thetak) + np.sin(thetan)*np.sin(thetak)*np.cos(phin)*np.cos(phik) + np.sin(thetan)*np.sin(thetak)*np.sin(phin)*np.sin(phik)


    summ = 0.25 * ( 1. - 3.*np.cos(thetak)**2 ) / ( 1. + xalpha + xc )
       
    first_term = 1 + k_dot_n**2
    second_term = 2. + 2.*k_dot_n**2 - 1./15.*summ

    res = x1s * ( 1 - Tg/Ts ) * np.sqrt( (1 + z)/10. ) * ( 26.4 * first_term - 0.128 * x1s * (Tg/Ts) * np.sqrt( (1 + z)/10. ) * second_term)

    return res/1000. #this is to make it to K from mK.

