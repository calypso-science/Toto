import numpy as np
from ...core.toolbox import dir_interval,get_number_of_loops
from windrose import WindroseAxes
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import matplotlib.cm as cm
from matplotlib import gridspec

def get_precentage(Ag,Ay,D,F,C,IncHiLow):
    E=np.zeros((int(len(Ay)-1),int(len(Ag)-1)))
    for i in range(0,len(Ay)-1):
        if (C=='centred') & (i==0):
            I=((D<Ay[i+1]) | (D>Ay[-1])).nonzero()[0]
        else:
            I=((D>=Ay[i]) & (D<Ay[i+1])).nonzero()[0]
        
        b=F[I]
        for j in range(0,len(Ag)-1):
            J=((b>=Ag[j]) & (b<Ag[j+1])).nonzero()[0]
            E[i,j]=len(J)
        

        if IncHiLow:
            E[i,-1]=len((b>=Ag[-2]).nonzero()[0])
        
    
    b=np.max(np.sum(E,1)/len(D)*100)
    return b

def do_roses(time,spd,drr,units,title,spdedg,quadran,time_blocking,fileout,show=True):
    if spdedg is None or len(spdedg)<1:
        spd_sorted=np.sort(spd)
        spdedg=[np.floor(min(spd*10.))/10.]+list(np.round(spd_sorted[(len(spd_sorted)*np.array([1,2,3,4,5,5.4,5.8,6])/6).astype(int)-1],1))
        spdedg=np.unique(spdedg)


    month=time.month
    number_of_loops,identifiers,month_identifier=get_number_of_loops(time_blocking)

    if quadran is None or len(quadran)<1:
        interval=dir_interval(22.5);

        b=[]
        for j in range(0,number_of_loops):
            #Pull out relevant indices for particular month/months
            index = np.in1d(month, month_identifier[j])
            if len(index.nonzero()[0])>1:
                SPD = spd[index]
                DIR = drr[index]
                b.append(get_precentage(spdedg,interval,DIR.values,SPD.values,'centred',True))
            
        b=np.array(b)
        dcircles=np.arange(1,25+.5,.5)
        ncircles=4
        d=max(b)/dcircles-ncircles
        quadran=[]
        try:
            i=(d==max(d[d<0])).nonzero()[0]
            d=dcircles[i]
            for i in range(0,ncircles):
                quadran.append(d[0]*i)
        
        except:
            quadran=np.arange(0,100+25,25)    


    fig = plt.figure(figsize=(8.27, 11.69), dpi=100)
    if number_of_loops==5: # seasons
        gs1 = gridspec.GridSpec(3, 3)
    elif number_of_loops>5: # monthly
        gs1 = gridspec.GridSpec(6, 3)
    else: # annual
        gs1 = gridspec.GridSpec(1,1)

    #gs2 = gridspec.GridSpec(5, 1)
    
    for j in range(0,number_of_loops):
        if j==number_of_loops-1:
            ax = fig.add_subplot(gs1[int(np.floor((number_of_loops/2)/2)),-1], projection="windrose",theta_labels=['E','NE',identifiers[j],'NW','W','SW','S','SE'])
        else:
            x=np.ceil(((j+1)/2))-1
            y=(np.mod((j%2)+1,2)-1)*-1
            ax = fig.add_subplot(gs1[int(x),int(y)], projection="windrose",theta_labels=['E','NE',identifiers[j],'NW','W','SW','','SE'])
        #Pull out relevant indices for particular month/months
        index = np.in1d(month, month_identifier[j])
        #ax = WindroseAxes.from_ax(fig=fig)
        ax.bar(drr[index],spd[index], normed=True, bins=np.array(spdedg),opening=0.8, edgecolor='white')               
        ax.set_yticks(quadran)
        
        if j==number_of_loops-1:
            ax.set_yticklabels(quadran)
            if number_of_loops==1:
                ax.set_legend(units=units,title=title,loc='lower right')
            else:
                ax.set_legend(units=units,title=title,loc='best',bbox_to_anchor=(0.5,-1.0, 0.5, 0.5))

    plt.subplots_adjust(bottom=0.02,top=.95,hspace=0.3)
    plt.show(block=~show)
    plt.savefig(fileout)


