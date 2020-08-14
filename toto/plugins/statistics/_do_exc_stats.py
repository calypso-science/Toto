
import matplotlib.dates as mpld
mpld.set_epoch('0000-12-31T00:00:00')
from matplotlib.dates import date2num,num2date
import numpy as np
from ...core.toolbox import dir_interval,get_increment,get_number_of_loops
from ...core.make_table import create_table
import pandas as pd
from itertools import groupby
def do_exc_stats(filename,time,mag,time_blocking,method,threshold,duration):


    ## Input
    sint=(time[2]-time[1]).seconds/(3600)
    gd_value=~np.isnan(mag)
    time=time[gd_value]
    mag=mag[gd_value]


    if 'persistence' in method:
        analysis_type='persistence'
        sign='>='
    else:
        analysis_type='ordinary'
        sign='<='

    if 'non' in method:
        sign='<'
        persistence_type='non-exceedence'
    else:
        sign='>'
        persistence_type='exceedence'


    printing_threshold=threshold
    if analysis_type=='persistence':
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
    for j in range(0,number_of_loops):
        #Pull out relevant indices for particular month/months
        index = np.in1d(month, month_identifier[j])
        #Calculate Exceedence/Non-exceedence matrices
        #make an infinity data matrix and slot only the desired data in
        if analysis_type=='persistence':
            exceedence=np.empty((len(threshold),len(duration)))
            data_matrix=np.Inf*np.zeros((len(mag),))
            data_matrix[index]=mag[index]
            for m in range(0,len(duration)):
                for n in range(0,len(threshold)):
                    exceedence[n,m]=persistent_percent_exceed(data_matrix,threshold[n],duration[m],sint,persistence_type)                
                    
            del data_matrix
            del m
            del n
            del index
        elif analysis_type == 'ordinary':
            exceedence=np.empty((len(threshold),number_of_loops))
            data_matrix=mag[index]
            nrecs=len(data_matrix)
            if nrecs>0:
                for m in range(0,len(threshold)):
                    if persistence_type=='exceedence':
                        exceedence[m,j]=(len((data_matrix >= threshold[m]).nonzero()[0])/nrecs)*100
                    elif persistence_type == 'non-exceedence':
                        exceedence[m,j]=(len((data_matrix <= threshold[m]).nonzero()[0])/nrecs)*100
            else:
                exceedence[:,0]=0


            del nrecs
            del index

        if analysis_type=='persistence':
            mat=np.empty((exceedence.shape[0]+1,exceedence.shape[1]+1),dtype = "object")
            mat[0,0]=identifiers[j]   
            for x in range(0,len(duration)):
                mat[0,x+1]='%.f' % (duration[x])

            for y in range(0,len(threshold)):
                mat[y+1,0]=sign+'%.1f' % (threshold[y])
        
            mat[1:,1:]=np.round(exceedence,2).astype(str)
            create_table(filename,identifiers[j],mat)
    
    if analysis_type=='ordinary':
            mat=np.empty((exceedence.shape[0]+1,exceedence.shape[1]+1),dtype = "object")
            mat[0,0]=''
            for x in range(0,len(identifiers)):
                mat[0,x+1]='%s' % (identifiers[x])
            for y in range(0,len(threshold)):
                mat[y+1,0]=sign+'%.1f' % (threshold[y])
        
            mat[1:,1:]=np.round(exceedence,2).astype(str)
            create_table(filename,time_blocking,mat)    
        
def persistent_percent_exceed(data,thresh,duration,sint,choice='exceedence'):
    '''%function [percentage_exceedence]=percent_exceed(data,thresh,duration,sint,varargin)
    %
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
    if choice == 'exceedence':
        data[((data>=thresh) & (data<np.Inf))]=np.NaN #find exceedences in data and set to NaN
    elif choice=='non-exceedence':
        data[(data<=thresh)]=np.NaN   #find exceedences in data and set to NaN


    a=np.isnan(data).astype(int)

    if np.sum(a)>0:                   #only continue if there are (non-)exceedences
        #b=np.diff(a)
        #c=(b==1).nonzero()[0] #                %index of (non-)exceedence starts
        #d=(b==-1).nonzero()[0]#               %index of (non-)exceedence ends
        #if len((np.isnan(data)).nonzero()[0])==nrecs:
        #    c=0
        #    d=nrecs
        #import pdb;pdb.set_trace()
        #if ~isempty(d) & np.isnan(data[0:d[0]]) & (len((np.isnan(data[0:d[0]])).nonzero()[0]))!=len(data):
        #    c=np.append(np.array(0),c)
       # 
       # 
       # if ~isempty(c) & np.isnan(data[c[-1]+1:len(data)]) & (len((np.isnan(data[c[-1]+1:nrecs])).nonzero()[0])!=len(data)):
       #     d=np.append(np.array(d),len(data))

        #find (non-)exceedence lengths and indices
        #peaklength=d-c;
        peaklength=[sum(1 for i in g) for k,g in groupby(a) if k==1]
        #peaksind=np.append(c+1,d)
        valid_peaks=(peaklength>duration)
        peaklength=np.array(peaklength)
        peaklength=peaklength[valid_peaks]
        if choice == 'exceedence':
            percentage_exceedence=(np.sum(peaklength)/nrecs)*100
        elif choice=='non-exceedence':
            percentage_exceedence=(np.sum(peaklength)/nrecs)*100;
                
    else:
        percentage_exceedence=0

    return percentage_exceedence

def do_exc_coinc_stats(filename,time,Xdata,Ydata,X_interval,Y_interval,time_blocking,analysis_method,exceed_type,binning):
    multiplier=100.
    if exceed_type=='exceedence':
        sign='>'
    else:
        sign='<'


    month=time.month
    number_of_loops,identifiers,month_identifier=get_number_of_loops(time_blocking)
    for j in range(0,number_of_loops):
        #Pull out relevant indices for particular month/months
        index = np.in1d(month, month_identifier[j])
        occurrence=np.empty((len(Y_interval)-1,len(X_interval)-1))
        #Calculate Joint Probability
        big_length=len(index.nonzero()[0]);
        if big_length>0:
            for k in range(0,len(X_interval)-1):
                if k==0:
                    if binning=='centred':
                        index1=(Xdata[index].values >= X_interval[k]) | (Xdata[index].values <= X_interval[k+1])
                    else:
                        index1=(Xdata[index].values >= X_interval[k]) & (Xdata[index].values <= X_interval[k+1])
            
                elif k >0:
                    index1=(Xdata[index].values > X_interval[k]) & (Xdata[index].values <= X_interval[k+1])
        
                for m in range(0,len(Y_interval)-1):
                    if m==1:
                        index2=index1 & (Ydata[index].values>=Y_interval[m]) & (Ydata[index].values<=Y_interval[m+1])
                    else:
                        index2=index1 & (Ydata[index].values>Y_interval[m]) & (Ydata[index].values<=Y_interval[m+1])

                    little_length=len(index2.nonzero()[0])
                    occurrence[m,k]=little_length/big_length
        
        #%%%%
        #transform to exceedance or non-exceedance
        #np.delete(occurrence, np.s_[-1], 1)

        occurrence[:,-1]=np.sum(occurrence,1)
        
        if exceed_type=='exceedance':
            occurrence = np.flipud(occurrence)
        
        occurrence=np.cumsum(occurrence,0)
        
        for o in range(0,occurrence.shape[1]):
            if occurrence[-1,o]!=0:
                occurrence[:,o]=np.round(occurrence[:,o]*multiplier/occurrence[-1,o],2);
            else:
                occurrence[:,o]=0

        if exceed_type=='exceedance':
            occurrence = np.flipud(occurrence)
        
        
        