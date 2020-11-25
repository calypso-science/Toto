
import numpy as np
from toto.core.toolbox import dir_interval,get_increment,get_number_of_loops
from toto.core.make_table import create_table
from matplotlib import pyplot as plt
from grid_strategy import strategies

class thermocline():
    def __init__(self, pandas_obj,time_blocking='Annual',funct=np.nanmean,val=0.1):
        self.data = pandas_obj
        
        self.profile={}

        self.xp=[float(x.split('_lev_')[-1]) for x in self.data.columns]
        self.x=np.hstack((np.arange(0,51,5),np.arange(100,901,100),np.arange(1000,5001,1000)))
        self.x=self.x[self.x<np.max(self.xp)]
        self.funct=funct
        self.val=val
        self.extract_thermocline(time_blocking)
    def extract_thermocline(self,time_blocking):
        time=self.data.index
        year=time.year
        month=time.month
        number_of_loops,identifiers,month_identifier=get_number_of_loops(time_blocking)
        
        for j in range(0,number_of_loops):
            #Pull out relevant indices for particular month/months
            index = np.in1d(month, month_identifier[j])
            if np.any(index):
                self.profile[identifiers[j]]={}
                yp=np.ones((len(self.xp)))*np.nan
                for i,val in enumerate(self.data.columns):
                    if self.funct.__name__=='nanpercentile' or self.funct.__name__=='nanquantile':
                        yp[i]=self.funct(self.data[val][index],val)
                    else:
                        yp[i]=self.funct(self.data[val][index])


                self.profile[identifiers[j]]=np.interp(self.x,self.xp,yp)

    def output_table(self,filename):
        months=list(self.profile.keys())
        number_of_loops=len(months)
        mat=np.empty((len(self.x)+1,number_of_loops+1),dtype = "object")
        mat[0,0]=self.funct.__name__
        mat[1:,0]=np.round(self.x,2).astype(str)
        for j in range(0,number_of_loops):
            #Pull out relevant indices for particular month/months
            mat[0,j+1]=months[j]
            mat[1:,j+1]=np.round(self.profile[months[j]],2).astype(str)

        create_table(filename,'profile',mat)


    def output_fig(self,figure_filename,xlabel='Temp [degC]',display=True):


        months=list(self.profile.keys())
        number_of_loops=len(months)
        
        spec = strategies.SquareStrategy().get_grid(number_of_loops)
        fig = plt.gcf()
        fig.set_dpi(100)
        fig.constrained_layout=True
        fig.set_figheight(11.69)
        fig.set_figwidth(8.27)
        xmin=np.inf
        xmax=-np.inf

        for month in months:
            xmin=min(xmin,np.nanmin(self.profile[month]))
            xmax=max(xmax,np.nanmax(self.profile[month]))

        for j,sub in enumerate(spec):
            ax = plt.subplot(sub)
            ax.plot(self.profile[months[j]],self.x*-1)

            ax.set_xlabel(xlabel)
            ax.set_ylabel('Water depth (m)')
            ax.set_title(months[j])
            ax.set_xlim(xmin,xmax)
        
        fig.align_labels()
      
        if display:
            plt.show(block=~display)

        plt.savefig(figure_filename)