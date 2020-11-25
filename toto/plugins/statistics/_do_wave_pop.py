import numpy as np
import copy
from scipy.special import erf
from numpy.matlib import repmat
from ...core.make_table import create_table
from ...core.toolbox import display_message
def do_wave_pop(time,Hs,Tm,Drr,Tp,Sw,method,dh,Ddir,tbins,exposure,drr_switch,fileout):

    display_message()


def export_table(filename,sheetname,pop,hbins,dbins):
    display_message()



def update_pop(pop,hbins,len,dt,exposure):

    display_message()

def wavepop(hs,tm,dt,dh,method,**varargin):
    '''wavepop: calculates a population of wave heights in bins of height and
    %         (optionally) direction
    %
    %pop=wavepop(hs,tm,dt,dh,{dp,ddir,SW})
    %
    %%%%%%INPUTS
    %hs         significant wave height
    %tm         mean period (zero crossing period - ~Tm02)
    %dt         time for which hs and tp are representative (in seconds)
    %
    %dh         size of wave height classification bins i.e. 0.25 gives 0-0.25,0.25-0.5 etc.
    %           or vector of bin edges e.g. [0 0.25 0.5 1.0 2.0];
    %method     1= height only, 2= height / direction, 3= height / Tp, 4=
    %           height / period'.
    %dp         optional input for the peak/mean direction (or period) of each sample
    %ddir       if dp specified - size of direction (or period) bins or bin edges
    %SW         optional - spectral width for LH distribution. if iswmpty(SW)=>
    %           uses Rayleigh distribution. 
    % 
    %%%%%%OUTUTS
    %pop        total number of waves in each bin- this is a vector for each height bin
    %           or a matrix if directions or period are specified
    %hbins      vector of wave height bin edges
    %dbins      vector of wave direction (or period if method == 3 or 4) bin edges 

    %Currently uses standard rayleigh distribution or Longuet-Higgins83 (is SW supplied) and assumes:
    %1. Total number of waves is the total time divided by mean period
    %2. All waves in a sample have the same peak/mean direction '''

    #total number of waves for each sample
    display_message()

def LH(h,HS,SW):
    #1D probability density for wave height taking into account spectral width
    #see LONGUET-HIGGINS 1983 p.247
    display_message()

def LH_2D(h,tt,HS,SW,TM):
    #2D probability density for wave height taking into account spectral width
    #see LONGUET-HIGGINS 1983 p.247
    #w = waitbar(0,'Estimating Longuet-Higgins joint probability distributions for each time step');
    display_message()