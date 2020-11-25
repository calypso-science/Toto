
import numpy as np
from ...core.toolbox import dir_interval,get_increment,get_number_of_loops,degToCompass
from ...core.make_table import create_table


def do_directional_stat(filename,funct,val,short_name,time,Xdata,Ydata,X_interval,time_blocking,binning):

    year=time.year
    month=time.month

    gd_data=~np.isnan(Xdata) | ~np.isnan(Ydata)

    Xdata=Xdata[gd_data]
    Ydata=Ydata[gd_data]
    year=year[gd_data]
    month=month[gd_data]

    #----------------------------------------
  
    number_of_loops,identifiers,month_identifier=get_number_of_loops(time_blocking)
    mat=np.empty((number_of_loops+1,len(X_interval)+1),dtype = "object")
    if funct.__name__=='nanpercentile' or funct.__name__=='nanquantile':
        mat[0,0]=funct.__name__.replace('nan','')+'(%.1f)'%val
    else:
        mat[0,0]=funct.__name__.replace('nan','')
    
    for x in range(0,len(X_interval)-1):
        mat[0,x+1]='%s' % degToCompass([X_interval[x],X_interval[x+1]])
    mat[0,x+2]='Total'
    
    for j in range(0,number_of_loops):
        #Pull out relevant indices for particular month/months
        mat[j+1,0]=identifiers[j]
        index = np.in1d(month, month_identifier[j])
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
        
                if np.any(index1):
                    if funct.__name__=='nanpercentile' or funct.__name__=='nanquantile':
                        mat[j+1,k+1]=np.round(funct(Ydata[index][index1],val),2).astype(str)
                    else:
                        mat[j+1,k+1]=np.round(funct(Ydata[index][index1]),2).astype(str)

            
            mat[j+1,k+2]=np.round(np.nanmax(Ydata[index]),2).astype(str)
            
            
    create_table(filename,short_name,mat)