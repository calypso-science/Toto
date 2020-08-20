
from matplotlib.dates import date2num,num2date
import numpy as np
import pandas as pd
from ...core.toolbox import get_number_of_loops
from itertools import groupby
from ...core.make_table import create_table
def do_workability(filename,data,Exc,duration,time_blocking,analysis):

    if 'non' in analysis:
        sign='<'
        persistence_type='non-exceedence'
    else:
        sign='>'
        persistence_type='exceedence'

    time=data.index
    sint=(time[2]-time[1]).seconds/(3600)
    d=date2num(time)
    new_date=np.arange(d[0],d[-1]+sint/24,sint/24.)    
    mag=data.to_numpy()  

    new_mag=np.nan*np.zeros((len(new_date),mag.shape[1]))
    index=np.round((d-new_date[0])/(sint/24))
    new_mag[index.astype(int),:]=mag
    mag=new_mag
    new_date=pd.date_range(start=time[0], end=time[-1]+(time[2]-time[1]),freq=str(int(sint*3600))+'s')

    month=new_date.month
    year=new_date.year

    number_of_loops,identifiers,month_identifier=get_number_of_loops(time_blocking)
    work=np.empty((number_of_loops,len(duration)))
    windows_number=np.empty((number_of_loops,len(duration)))
    avg_window_length=np.empty((number_of_loops,len(duration)))
    for j in range(0,number_of_loops):
        #Pull out relevant indices for particular month/months
        index = np.in1d(month, month_identifier[j])
        number_of_years=len(year[index].unique())
        #Calculate Exceedence/Non-exceedence matrices
        #make an infinity data matrix and slot only the desired data in
        data_matrix=np.Inf*np.zeros((mag.shape))

        data_matrix[index]=mag[index]
        for m in range(0,len(duration)):
            work[j,m],windows_number[j,m],avg_window_length[j,m]=persistent_workability(data_matrix,Exc,duration[m],sint,persistence_type,number_of_years);



    mat=np.empty((work.shape[0]+1,work.shape[1]+1),dtype = "object")
    mat[0,0]=''   
    for x in range(0,len(duration)):
        mat[0,x+1]=sign+'%.f' % (duration[x])

    for y in range(0,len(identifiers)):
        mat[y+1,0]='%s' % (identifiers[y])

    mat[1:,1:]=np.round(work,2).astype(str)
    create_table(filename,'work',mat)
    mat[1:,1:]=np.round(windows_number,2).astype(str)
    create_table(filename,'windows_number',mat)
    mat[1:,1:]=np.round(avg_window_length,2).astype(str)
    create_table(filename,'windows_length',mat)


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

    duration=np.ceil(duration/sint)

    data[data==0]=1e-10
    data[np.isnan(data)]=np.Inf
    nrecs=len(((data>0) & (data<np.Inf)).nonzero()[0])
    for n in range(0,data.shape[1]):
        if choice == 'exceedence':
            data[((data[:,n]>=thresh[n]) & (data[:,n]<np.Inf)),n]=np.NaN #find exceedences in data and set to NaN
        elif choice=='non-exceedence':
            data[(data[:,n]<=thresh[n]),n]=np.NaN   #find exceedences in data and set to NaN


    a=np.all(np.isnan(data),1).astype(int)
    if np.sum(a)>0:                   #only continue if there are (non-)exceedences

        peaklength=[sum(1 for i in g) for k,g in groupby(a) if k==1]
        #peaksind=np.append(c+1,d)
        valid_peaks=(peaklength>duration)
        peaklength=np.array(peaklength)
        peaklength=peaklength[valid_peaks]


        windows_number=len(valid_peaks)/number_of_years
        percentage_workability=(np.nansum(peaklength)/nrecs)*100
        avg_window_length=np.nanmean(peaklength*sint)

                
    else:
        percentage_workability=0
        windows_number=0
        avg_window_length=0

    return percentage_workability,windows_number,avg_window_length