import numpy as np
from ...core.make_table import create_table

def do_comp_stats(output_name,hindcast,measured,short_name=''):

    gd=(~np.isnan(hindcast)) & (~np.isnan(measured))
    stats=np.empty((6,3),dtype="object")
    stats[0,0]='MAE'
    stats[1,0]='RMSE'
    stats[2,0]='MRAE'
    stats[3,0]='BIAS'
    stats[4,0]='SI'
    stats[5,0]='IOA'
    stats[0,1]='Mean Absolute Error'
    stats[1,1]='Root Mean Square Error'
    stats[2,1]='Mean Relative Absolute Erro'
    stats[3,1]='BIAS'
    stats[4,1]='Scatter Index'
    stats[5,1]='Index of Agreement'

  
    stats[0,2]='%.2f' % np.mean(np.abs(hindcast[gd]-measured[gd])) #Mean absolute error: 
    stats[1,2]='%.2f' % np.sqrt(np.mean(hindcast[gd]-measured[gd])**2) #%RMS error
    stats[2,2]='%.2f' % np.mean(np.abs((hindcast[gd]-measured[gd])/measured[gd])) #%MRAE
    stats[3,2]='%.2f' % np.mean((hindcast[gd]-measured[gd])) #BIAS
    stats[4,2]='%.2f' % (np.sqrt(np.mean(hindcast[gd]-measured[gd])**2))/(np.mean(measured[gd])) #SI
    stats[5,2]='%.2f' % 1-(np.sum((np.abs(hindcast-measured))**2))/\
                        (np.sum((np.abs(hindcast-np.mean(measured))+np.abs(measured-np.mean(measured)))**2))        



    create_table(output_name,short_name,stats)