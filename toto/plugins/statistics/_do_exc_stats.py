
import matplotlib.dates as mpld

try:
    mpld.set_epoch('0000-12-31T00:00:00')
except:
    pass
    
from ...core.toolbox import display_message
from matplotlib.dates import date2num,num2date
import numpy as np
from ...core.toolbox import dir_interval,get_increment,get_number_of_loops
from ...core.make_table import create_table
import pandas as pd
from itertools import groupby
from calendar import monthrange
import copy
def to_workability(peakind,fac,index,nyear):
    display_message()
    


def do_window_stats(filename,time,mag,time_blocking,method,threshold,duration):


    display_message()
    

def do_exc_stats(filename,time,mag,time_blocking,method,threshold,duration,mag_name):


    display_message()   
        
def persistent_percent_exceed(data0,thresh,duration,sint,choice='exceedence'):
    '''%function [percentage_exceedence]=percent_exceed(data,thresh,duration,sint,varargin)
    %
    %varagrin can either be 'exceedence' or 'non-exceedence', the default is exceedence
    %
    %determines the percentage of exceedence/non-exceedence greater/lesser than or equal
    %to a threshold value for a given duration
    %
    %sint defines the interval at which the data is sampled in hours
    %duration defines minimum duration of an event in hours'''

    display_message()

############33
def do_exc_coinc_stats(filename,time,Xdata,Ydata,X_interval,Y_interval,time_blocking,analysis_method,exceed_type,binning):
    display_message()
