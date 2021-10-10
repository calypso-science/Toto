import numpy as np

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import matplotlib.colors as colors
import matplotlib.cm as cmx
from ...core.toolbox import get_number_of_loops,degToCompass
from matplotlib import gridspec
from grid_strategy import strategies

def get_perc(s,SPD):
    perc=np.empty(shape=(len(s)-1,1))
    for h in range(0,len(s)-1):
        nombre=((SPD>=s[h]) & (SPD<s[h+1])).nonzero()[0]
        nom=len(nombre)/(s[h+1]-s[h]) #number of occurence per unit of magnitude
        perc[h]=(nom)*100

    return perc

def do_perc_of_occurence(time,mag,drr,mag_interval,xlabel,time_blocking,dir_int,fileout,show):

    ## Input
    gd_value=~np.isnan(mag)
    time=time[gd_value]
    mag=mag[gd_value]
    if drr is not None:
    	drr=drr[gd_value]
    else:
        drr=np.ones((len(mag),))
        dir_int=[0,360]



    if isinstance(mag_interval,int) or  isinstance(mag_interval,float):
        s=np.arange(0,np.max(mag),mag_interval)
    elif isinstance(mag_interval,list):
        if len(mag_interval)<2:
            s=np.linspace(0,np.max(mag),10)
        else:
            s=np.array(mag_interval)
    else:
        s=np.linspace(0,np.max(mag),10)


    month=time.month
    number_of_loops,identifiers,month_identifier=get_number_of_loops(time_blocking)


    index=[]
    nj=[]
    for j in range(0,number_of_loops):
        tmp=np.in1d(month, month_identifier[j])
        if np.any(tmp):
            #index .append(tmp)
            nj.append(j)

    number_of_real_loops=len(nj)

    spec = strategies.SquareStrategy().get_grid(number_of_real_loops)
    fig = plt.gcf()
    fig.set_dpi(100)
    fig.constrained_layout=True
    fig.set_figheight(11.69)
    fig.set_figwidth(8.27)



    for i,sub in enumerate(spec):
        ax = plt.subplot(sub)

        #Pull out relevant indices for particular month/months
        index = np.in1d(month, month_identifier[nj[i]])
        big_length=len(index.nonzero()[0]);
        if big_length>0:           
            SPD = mag[index]      
            DIR = drr[index]
            

            jet = cm = plt.get_cmap('jet') 
            cNorm  = colors.Normalize(vmin=0, vmax=len(dir_int)-2)
            scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)

            for jj in range(0,len(dir_int)-1):
                if dir_int[jj+1] <= dir_int[jj]:
                    D=np.logical_or(np.mod(DIR,360)>dir_int[jj],np.mod(DIR,360)<=dir_int[jj+1]);
                else:
                    D=(np.mod(DIR,360)>dir_int[jj]) & (np.mod(DIR,360)<=dir_int[jj+1]);
                
                colorVal = scalarMap.to_rgba(jj)
                perc=get_perc(s,SPD[D])/big_length
                plt.plot(s[:-1]+np.diff(s)/2,perc,color=colorVal,label=degToCompass([dir_int[jj],dir_int[jj+1]]))
 


        ax.set_title(identifiers[nj[i]])

        if i==number_of_real_loops-1 and len(dir_int)>2:
            # if number_of_loops>3 and number_of_loops<10:
            #     ax.legend(loc='best',bbox_to_anchor=(0.6, -0.4),ncol=len(dir_int)-1)#bbox_to_anchor=(0.8,-1.0, 0.5, 0.5))
            # elif number_of_loops>10:
            #     ax.legend(loc='best',bbox_to_anchor=(0.6, -3.4),ncol=len(dir_int)-1)#bbox_to_anchor=(0.8,-1.0, 0.5, 0.5))
            # else:
                ax.legend(loc='best')

         

        #if int(y)==0:
        ax.set_ylabel('% Occurence')

        #if int(x)==maxx :
        ax.set_xlabel(xlabel)

    fig.align_labels()

    # if number_of_loops>10:
    #     plt.subplots_adjust(left=0.075,right=0.970,bottom=0.075,top=0.97,hspace=.5,wspace=0.415)
    #     ax.set_xlabel(xlabel)
        
    # elif number_of_loops>2 and number_of_loops<10:
    #     plt.subplots_adjust(left=0.08,right=0.975,bottom=0.05,top=0.7,hspace=.5,wspace=0.3)
    #     ax.set_xlabel(xlabel)
    # else:
    #     plt.subplots_adjust(bottom=0.05,top=.95,hspace=.5)

    plt.savefig(fileout)
    if show:
        plt.show()
   

