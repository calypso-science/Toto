import os
import numpy as np
from ...core.make_table import create_table
from ...core.toolbox import get_number_of_loops,degToCompass
from scipy.signal import find_peaks
from matplotlib import pyplot as plt
plt.style.use('bmh')
import matplotlib.colors as colors
import matplotlib.cm as cmx
from matplotlib import gridspec
import matplotlib.dates as mdate
import copy
from grid_strategy import strategies
import scipy.stats as ws
from ._estimation import FitDistribution


def sub_table(stats,varname,rp):
    
    dds= stats.keys()
    rvs=len(rp)
    mat=np.empty((rvs+2,len(dds)+1),dtype = "object")
    mat[0,0]=varname
    for i,dd in enumerate(dds):
        mat[0,i+1]=dd
        mat[1:1+rvs,i+1]=np.round(stats[dd][varname]['magex'],2).astype(str)


    mat[1:1+rvs,0]=np.round(rp).astype(str)
    mat[-1,:]=''
    return mat


def sub_table_shape(stats,varname,fitting):
    
    dds= stats.keys()
    rows=['fitting','method','scale','shape']
    mat=np.empty((len(rows)+2,len(dds)+1),dtype = "object")
    mat[0,0]=varname
    mat[1:len(rows)+1,0]=rows
    mat[1,1]=fitting
    mat[2,1]=stats['Omni'][varname]['phat'].method
    for i,dd in enumerate(dds):
        mat[0,i+1]=dd
        mat[3,i+1]=np.round(stats[dd][varname]['scale'],4).astype(str)
        mat[4,i+1]=np.round(stats[dd][varname]['shape'],4).astype(str)


    mat[-1,:]=''
    return mat

def do_fitting(mag,fitting,method,loc=None):
    if loc is None:
        loc=np.nanmin(mag)*.999

    if fitting.lower()=='weibull':
        phat = ws.weibull_min.fit2(mag,floc=loc,alpha=0.05,method=method.lower())
        print(phat)
        scale=phat.par[-1]
        shape=phat.par[0]
    elif fitting.lower() == 'gumbel':
        phat = ws.gumbel_r.fit2(mag,method=method,alpha=0.05)
        scale=phat.par[0]
        shape=phat.par[-1]
    elif fitting.lower() == 'gpd':
        phat = ws.genpareto.fit2(mag,floc=loc,method=method.lower(),alpha=0.05)
        scale=phat.par[-1]
        shape=phat.par[0]*-1

    elif fitting.lower() == 'gev':
        phat = ws.genextreme.fit2(mag,floc=loc,method=method.lower(),alpha=0.05)
        scale=phat.par[-1]
        shape=phat.par[0]

    else:
        assert 'Fitting %s not recognize' % fitting

    return phat,scale,shape


class ExtremeBase:
    def __init__(self, pandas_obj):
        self.data = pandas_obj
        self.dfout = self.data.copy()
        self.dfout['Hmp']=np.NaN
        self.dfout['Cmp']=np.NaN
        self.dfout['LnN']=np.NaN
        self.sint=(self.data.index[1]-self.data.index[0]).total_seconds()
        if 'time' in self.dfout:
            del self.dfout['time']
        self.peaks_index= {}
        self.eva_stats= {}
        self.nyear=self.sint*len(self.dfout['Hmp'])/(24*365.25*3600) #; %length of time series in years
        if hasattr(self.data,'filename'):
            self.file=os.path.splitext(self.data.filename)[0]+'_'
        else:
            self.file='_'

    def _get_shape(self,mag,fitting,method,time_blocking,):

        el_res=self.dfout[mag]

        number_of_loops,identifiers,month_identifier=get_number_of_loops(time_blocking)
        months=self.dfout.index.month
        idx=np.arange(0,len(months))
        mag_values=self.dfout[mag]
        for j in range(0,number_of_loops):
        #Pull out relevant indices for particular month/months
            if identifiers[j] in self.peaks_index:
                peak= self.peaks_index[identifiers[j]]['Omni']

                if identifiers[j] not in self.eva_stats:
                    self.eva_stats[identifiers[j]]={}
                    self.eva_stats[identifiers[j]]['Omni']={}

                if mag not in self.eva_stats[identifiers[j]]['Omni']:
                    self.eva_stats[identifiers[j]]['Omni'][mag]={}


                y=self.dfout[mag][peak].values
                y=y[~np.isnan(y)]
                el_resJP=y

                loc=min(y)-0.01;
                phat,scale,shape=do_fitting(y,fitting,method,loc=loc)
                self.eva_stats[identifiers[j]]['Omni'][mag]['phat']=phat
                self.eva_stats[identifiers[j]]['Omni'][mag]['scale']=scale
                self.eva_stats[identifiers[j]]['Omni'][mag]['shape']=shape
                self.eva_stats[identifiers[j]]['Omni'][mag]['el_resJP']=el_resJP



    def _clean_peak(self):
        keys=list(self.peaks_index.keys())
        for key in keys:
            if len(self.peaks_index[key])==0:
                self.peaks_index.pop(key)

    def _get_peaks(self,mag,drr=None,time_blocking='Annual',directional_interval=[0,360],peaks_options={},min_peak=30):

        if drr == None or drr=='':
            drr='direction_optional'
            self.dfout['direction_optional']=np.ones((len(self.dfout[mag].values),))*20

        
        number_of_loops,identifiers,month_identifier=get_number_of_loops(time_blocking)

        months=self.dfout.index.month
        idx=np.arange(0,len(months))
        drr_values=self.dfout[drr]
        mag_values=self.dfout[mag]

        for j in range(0,number_of_loops):
        #Pull out relevant indices for particular month/months
            index1 = np.in1d(months, month_identifier[j])
            self.peaks_index[identifiers[j]]={}

            for jj in range(0,len(directional_interval)):

                if jj==len(directional_interval)-1:
                    index2=drr_values>-1
                    dir_label='Omni'
                else:
                    dir_label=degToCompass([directional_interval[jj],directional_interval[jj+1]])
                    if directional_interval[jj+1] <= directional_interval[jj]:
                        index2=np.logical_or(drr_values>directional_interval[jj],drr_values<=directional_interval[jj+1])
                    else:
                        index2=(drr_values>directional_interval[jj]) & (drr_values<=directional_interval[jj+1])
                index=np.logical_and(index1,index2)
                if np.any(index):
                    tmp=mag_values.values.copy()
                    tmp[~index]=0
                    pk_idx=find_peaks(tmp,**peaks_options)[0]
                    if len(pk_idx)>min_peak:
                        self.peaks_index[identifiers[j]][dir_label]=pk_idx

    def _plot_cdfs(self,mag,drr='Omni',display=False,folder=os.getcwd()):

        months=list(self.peaks_index.keys())
        number_of_loops=len(months)
        spec = strategies.SquareStrategy().get_grid(number_of_loops)
        fig = plt.gcf()
        fig.set_dpi(100)
        fig.constrained_layout=True
        fig.set_figheight(11.69)
        fig.set_figwidth(8.27)

        for j,sub in enumerate(spec):
            if drr in self.eva_stats[months[j]]:
                ax = plt.subplot(sub)
                stat=self.eva_stats[months[j]][drr][mag]
                ws.probplot(stat['phat'].data, stat['phat'].par, dist=stat['phat'].dist.name, plot=ax)
                ax.set_title(months[j]+': '+drr)


        fig.align_labels()
        # if number_of_loops>10:
        #     plt.subplots_adjust(left=0.075,right=0.970,bottom=0.1,top=0.97,hspace=.5,wspace=0.415)            
        # elif number_of_loops>2 and number_of_loops<10:
        #     plt.subplots_adjust(left=0.08,right=0.975,bottom=0.1,top=0.7,hspace=.5,wspace=0.3)
        # else:
        #     plt.subplots_adjust(bottom=0.05,top=.95,hspace=.5)
      


        plt.savefig(os.path.join(folder,self.file+'cdf_'+mag+'_'+drr+'.png'))
        if display:
            plt.show()

    def _plot_peaks(self,mag,display=False,folder=os.getcwd()):
        months=list(self.peaks_index.keys())
        number_of_loops=len(months)


        spec = strategies.SquareStrategy().get_grid(number_of_loops)
        fig = plt.gcf()
        fig.set_dpi(100)
        fig.constrained_layout=True
        fig.set_figheight(11.69)
        fig.set_figwidth(8.27)


        for j,sub in enumerate(spec):
            ax = plt.subplot(sub)

            dir_ints=self.peaks_index[months[j]].keys()
            jet = cm = plt.get_cmap('jet') 
            cNorm  = colors.Normalize(vmin=0, vmax=len(dir_ints))
            scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
            plt.plot(self.dfout.index.values,self.dfout[mag].values,'k',linewidth=0.1)

            for jj,dir_int in enumerate(dir_ints):
                if len(dir_ints)==1 or dir_int!='Omni':
                    pk=self.peaks_index[months[j]][dir_int]
                    colorVal = scalarMap.to_rgba(jj)
                    plt.plot(self.dfout.index.values[pk],self.dfout[mag].values[pk],'+',color=colorVal,label=dir_int)
            
            locator = mdate.YearLocator()
            ax.xaxis.set_major_locator(locator)
            ax.set_title(months[j])

            if j==number_of_loops-1 and len(dir_int)>2:
               ax.legend(loc='best')    

            ax.set_ylabel('%s'%mag)

        fig.align_labels()

        # if number_of_loops>10:
        #     plt.subplots_adjust(left=0.075,right=0.970,bottom=0.1,top=0.97,hspace=.5,wspace=0.415)            
        # elif number_of_loops>2 and number_of_loops<10:
        #     plt.subplots_adjust(left=0.08,right=0.975,bottom=0.1,top=0.7,hspace=.5,wspace=0.3)
        # else:
        #     plt.subplots_adjust(bottom=0.05,top=.95,hspace=.5)
      
       
        plt.savefig(os.path.join(folder,self.file+mag+'_peaks.png'))
        if display:
            plt.show()

    def _export_shape_as_xls(self,magnitudes,fitting,filename):

        months=self.eva_stats.keys()
        for i,month in enumerate(months):
            for j,var in enumerate(magnitudes):
                if var in self.eva_stats[month]['Omni']:
                    mat0=sub_table_shape(self.eva_stats[month],var,fitting)
                    if 'mat' not in locals():
                        mat=copy.deepcopy(mat0)
                    else:
                        try:
                            mat=np.concatenate((mat,mat0))
                        except:
                            import pdb;pdb.set_trace()

            create_table(filename,month,mat)
            del mat

    def _export_as_xls(self,magnitudes,rp,filename):

        months=self.eva_stats.keys()
        for i,month in enumerate(months):
            for j,var in enumerate(magnitudes):
                if var in self.eva_stats[month]['Omni']:

                    mat0=sub_table(self.eva_stats[month],var,rp)
                    if 'mat' not in locals():
                        mat=copy.deepcopy(mat0)
                    else:
                        try:
                            mat=np.concatenate((mat,mat0))
                        except:
                            import pdb;pdb.set_trace()

            create_table(filename,month,mat)
            del mat

    def _plot_cdfs(self,mag,drr='Omni',display=False,folder=os.getcwd()):

        months=list(self.peaks_index.keys())
        number_of_loops=len(months)
        spec = strategies.SquareStrategy().get_grid(number_of_loops)
        fig = plt.gcf()
        fig.set_dpi(100)
        fig.constrained_layout=True
        fig.set_figheight(11.69)
        fig.set_figwidth(8.27)

        for j,sub in enumerate(spec):
            if drr in self.eva_stats[months[j]]:
                ax = plt.subplot(sub)
                stat=self.eva_stats[months[j]][drr][mag]
                ws.probplot(stat['phat'].data, stat['phat'].par, dist=stat['phat'].dist.name, plot=ax)
                ax.set_title(months[j]+': '+drr)


        fig.align_labels()
        # if number_of_loops>10:
        #     plt.subplots_adjust(left=0.075,right=0.970,bottom=0.1,top=0.97,hspace=.5,wspace=0.415)            
        # elif number_of_loops>2 and number_of_loops<10:
        #     plt.subplots_adjust(left=0.08,right=0.975,bottom=0.1,top=0.7,hspace=.5,wspace=0.3)
        # else:
        #     plt.subplots_adjust(bottom=0.05,top=.95,hspace=.5)
      


        plt.savefig(os.path.join(folder,self.file+'cdf_'+mag+'_'+drr+'.png'))
        if display:
            plt.show()
