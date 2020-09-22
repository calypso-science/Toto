import numpy as np
from toto.core.toolbox import dir_interval,get_increment,get_number_of_loops
from toto.core.make_table import create_table
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib import gridspec
from grid_strategy import strategies

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

def plot_occurence(tm,hs,occurrence,show,fileout,identifiers,xlabel,ylabel):

    number_of_loops=occurrence.shape[0]
    tm_bin=tm[1]-tm[0]
    hs_bin=hs[1]-hs[0]

    index=[]
    nj=[]
    for j in range(0,number_of_loops):
        if ~np.all(np.isnan(occurrence[j])):
            #index .append(tmp)
            nj.append(j)

    number_of_real_loops=len(nj)

    spec = strategies.SquareStrategy().get_grid(number_of_real_loops)
    fig = plt.gcf()
    fig.set_dpi(100)
    fig.constrained_layout=True
    fig.set_figheight(11.69)
    fig.set_figwidth(8.27)


    for j,sub in enumerate(spec):
        ax = plt.subplot(sub)
        plt.imshow(occurrence[nj[j],:,:], origin = 'lower',  extent = [tm[0], tm[-1], hs[0], hs[-1]],vmin=0,vmax=np.nanmax(occurrence))
        plt.colorbar()

        ax.set_xticks(tm)
        ax.set_yticks(hs)
        ax.grid()
        if number_of_real_loops==1:
            for i in range(0,len(tm)-1):
                for m in range(0,len(hs)-1):
                    if occurrence[nj[j],m,i]>0:
                        plt.text(tm[i]+tm_bin/2,hs[m]+hs_bin/2,str(occurrence[nj[j],m,i]),va='center',ha='center',FontWeight='demi',FontSize=8);
        
        #if identifiers[nj[j]].lower()=='annual':
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(identifiers[nj[j]])



    

    # if number_of_loops>10:
    #     plt.subplots_adjust(left=0.075,right=0.970,bottom=0.075,top=0.97,hspace=.5,wspace=0.415)
        
    # elif number_of_loops>2 and number_of_loops<10:
    #     plt.subplots_adjust(left=0.08,right=0.975,bottom=0.05,top=0.7,hspace=.5,wspace=0.3)

    # else:
    #     plt.subplots_adjust(bottom=0.05,top=.95,hspace=.5)

    if show:
        plt.show(block=~show)
    plt.savefig(fileout)


def _do_joint_prob_plot(filename,time,Xdata,Ydata,X_interval,Y_interval,time_blocking,show,xlabel,ylabel,multiplier=1000):

    year=time.year
    month=time.month

    gd_data=~np.isnan(Xdata) & ~np.isnan(Ydata)

    Xdata=Xdata[gd_data]
    Ydata=Ydata[gd_data]
    year=year[gd_data]
    month=month[gd_data]

    #----------------------------------------
  
    number_of_loops,identifiers,month_identifier=get_number_of_loops(time_blocking)
    occurrence=np.empty((int(number_of_loops),len(Y_interval)-1,len(X_interval)-1))
    for j in range(0,number_of_loops):
        #Pull out relevant indices for particular month/months
        index = np.in1d(month, month_identifier[j])
        
        #Calculate Joint Probability
        big_length=len(index.nonzero()[0]);
        if big_length>0:
            for k in range(0,len(X_interval)-1):
                index1=(Xdata[index].values > X_interval[k]) & (Xdata[index].values <= X_interval[k+1])       
                for m in range(0,len(Y_interval)-1):
                    if m==1:
                        index2=index1 & (Ydata[index].values>=Y_interval[m]) & (Ydata[index].values<=Y_interval[m+1])
                    else:
                        index2=index1 & (Ydata[index].values>Y_interval[m]) & (Ydata[index].values<=Y_interval[m+1])

                    little_length=len(index2.nonzero()[0])
                    occurrence[j,m,k]=little_length/big_length

    occurrence=occurrence*multiplier
    occurrence=np.round(occurrence,2)
    occurrence[occurrence==0]=np.nan
    plot_occurence(X_interval,Y_interval,occurrence,show,filename,identifiers,xlabel,ylabel)