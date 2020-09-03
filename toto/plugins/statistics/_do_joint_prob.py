import numpy as np
from ...core.toolbox import dir_interval,get_increment,get_number_of_loops
from ...core.make_table import create_table

def do_joint_prob(filename,time,Xdata,Ydata,X_interval,Y_interval,time_blocking,binning,multiplier=1000):

    year=time.year
    month=time.month

    gd_data=~np.isnan(Xdata) & ~np.isnan(Ydata)

    Xdata=Xdata[gd_data]
    Ydata=Ydata[gd_data]
    year=year[gd_data]
    month=month[gd_data]

    #----------------------------------------
  
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

            occurrence=occurrence*multiplier

            occurrence[-1,:]=np.sum(np.round(occurrence,int(-np.log10(multiplier)+4)),0)
            occurrence[:,-1]=np.sum(np.round(occurrence,int(-np.log10(multiplier)+4)),1)
            occurrence[-1,-1]=multiplier

            mat=np.empty((occurrence.shape[0]+1,occurrence.shape[1]+1),dtype = "object")
            mat[0,0]=identifiers[j]
            for x in range(0,len(X_interval)-1):
                mat[0,x+1]='%.1f-%.1f' % (X_interval[x],X_interval[x+1])
            mat[0,-1]='Total'
            for y in range(0,len(Y_interval)-1):
                mat[y+1,0]='%.1f-%.1f' % (Y_interval[y],Y_interval[y+1])
            mat[-1,0]='Total'
            # mat[1:,0]=Y_interval[:-1]
            mat[1:,1:]=np.round(occurrence,2).astype(str)
            create_table(filename,identifiers[j],mat)