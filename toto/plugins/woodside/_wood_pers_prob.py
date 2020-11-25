


from matplotlib.dates import date2num,num2date
import numpy as np
from ...core.toolbox import dir_interval,get_increment,get_number_of_loops
from ...core.make_table import create_table
import pandas as pd
from itertools import groupby
from calendar import monthrange
import copy
from toto.plugins.statistics._do_exc_stats import persistent_percent_exceed
from ...core.toolbox import display_message

def do_perc_stats(filename,time,mag,time_blocking,method,threshold,duration):


    display_message()