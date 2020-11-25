
from matplotlib.dates import date2num,num2date
import numpy as np
import pandas as pd
from ...core.toolbox import get_number_of_loops
from itertools import groupby
from ...core.make_table import create_table
from ...core.toolbox import display_message

def do_workability(filename,data,Exc,duration,time_blocking,analysis):

    display_message()


def persistent_workability(data,thresh,duration,sint,choice,number_of_years):
    '''function [percentage_exceedence]=persistent_workability(data,thresh,duration,sint,varargin)
    %similar as persistent_percent_exceed but with 2 thresholds corresponding
    %to two input paramter (e.g. hs and wspd)
    %varagrin can either be 'exceedence' or 'non-exceedence', the default is exceedence
    %
    %determines the percentage of exceedence/non-exceedence greater/lesser than or equal
    %to a threshold value for a given duration
    %
    %sint defines the interval at which the data is sampled in hours
    %duration defines minimum duration of an event in hours'''

    display_message()