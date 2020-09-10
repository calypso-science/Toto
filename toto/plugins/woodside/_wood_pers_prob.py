


from matplotlib.dates import date2num,num2date
import numpy as np
from ...core.toolbox import dir_interval,get_increment,get_number_of_loops
from ...core.make_table import create_table
import pandas as pd
from itertools import groupby
from calendar import monthrange
import copy
from toto.plugins.statistics._do_exc_stats import persistent_percent_exceed

def do_perc_stats(filename,time,mag,time_blocking,method,threshold,duration):


    ## Input
    sint=(time[2]-time[1]).seconds/(3600)
    gd_value=~np.isnan(mag)
    time=time[gd_value]
    mag=mag[gd_value].values



    analysis_type='persistence'


    if 'non' in method:
        sign='<'
        persistence_type='non-exceedence'
    else:
        sign='>'
        persistence_type='exceedence'


    printing_threshold=threshold

    #we create full datasets of the mag and date
    #that don't have time gaps for persistence analysis
    d=date2num(time)
    new_date=np.arange(d[0],d[-1]+sint/24,sint/24.)       
    new_mag=np.nan*np.zeros((len(new_date),))
    index=np.round((d-new_date[0])/(sint/24))
    new_mag[index.astype(int)]=mag
    mag=new_mag
    new_date=pd.date_range(start=time[0], end=time[-1],freq=str(int(sint*3600))+'s')
            

    #this is because if using persistence (non-) exceedence NaN values are set to zero and
    #so zero values are made small but non-zero this happens in the function that determines
    #(non-)exceedence butr here we need to set the threshold lower so that it captures these values
    
    if threshold[0]==0:
            threshold[0]=1e-10

    month=time.month
    number_of_loops,identifiers,month_identifier=get_number_of_loops(time_blocking)
    for n in range(0,len(threshold)):
        for j in range(0,number_of_loops):
            #Pull out relevant indices for particular month/months
            index = np.in1d(month, month_identifier[j])
            #Calculate Exceedence/Non-exceedence matrices
            #make an infinity data matrix and slot only the desired data in
            exceedence=np.empty((number_of_loops,len(duration)))
            data_matrix=np.Inf*np.zeros((len(mag),))
            data_matrix[index]=mag[index]
            for m in range(0,len(duration)):
                exceedence[j,m],_=persistent_percent_exceed(data_matrix,threshold[n],duration[m],sint,persistence_type)                
                        
            del data_matrix
            del m
            del index


        mat=np.empty((exceedence.shape[0]+1,exceedence.shape[1]+1),dtype = "object")
        mat[0,0]=''   
        for x in range(0,len(duration)):
            mat[0,x+1]='%.f' % (duration[x])

        for y in range(0,len(identifiers)):
            mat[y+1,0]='%s' % (identifiers[y])
    
        mat[1:,1:]=np.round(exceedence,2).astype(str)
        create_table(filename,sign+str(threshold[n]),mat)
    
