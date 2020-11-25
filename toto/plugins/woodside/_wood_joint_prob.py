import numpy as np
from toto.core.toolbox import dir_interval,get_increment,get_number_of_loops
from toto.core.make_table import create_table
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from ...core.toolbox import display_message

def do_joint_prob(filename,time,Xdata,Ydata,X_interval,Y_interval,time_blocking,binning,multiplier=1000):

    display_message()

