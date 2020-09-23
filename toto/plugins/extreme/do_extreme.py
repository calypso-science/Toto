import pandas as pd
import os
from ...core.toolbox import dir_interval,get_increment,get_number_of_loops,degToCompass,wavenuma,PolyArea
from ...core.wavestats import calc_slp
from ...core.make_table import create_table
import numpy as np
from scipy.signal import find_peaks
from matplotlib import pyplot as plt
plt.style.use('bmh')
import matplotlib.colors as colors
import matplotlib.cm as cmx
from matplotlib import gridspec
import matplotlib.dates as mdate
from ._EVA_funct import *
from scipy.stats import norm
import copy
from grid_strategy import strategies

@pd.api.extensions.register_dataframe_accessor("Extreme")



class Extreme:
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

    def extreme_water_elevation(self,tide='tide',surge='surge',
        args={'Fitting distribution':{'Weibull':True,'Gumbel':False,'GPD':False,'GEV':False},
         'Method':{'pkd':False,'pwm':False,'mom':False,'ml':True},
         'Surge':{'Positive only':False,'Negative only':False,'Both (neg and pos)':True},
         'Return period':[1,10,25,50,100],
         'threshold type':{'percentile':True,'value':False},
         'threshold value':95.0,
         'Minimum number of peaks over threshold': 30,
         'Minimum time interval between peaks (h)':24.0,
         'Time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
         'Display peaks':{'On':True,'Off':False},
         'Display CDFs':{'On':True,'Off':False},
         'folder out':os.getcwd()
         }):


        '''%This function is used for extreme value analysis of total still water 
        %elevation (surge + tide). Inputs must be surge and tide level (in the 
        %same unit).
        %The method complies with ISO recommendations: return period values are 
        %estimated by fitting a distribution to the empirical distribution 
        %obtained by combining the joint frequency distribution of tidal and surge 
        %elevations.'''

        self.dfout['positive_surge']=self.data[surge]
        self.dfout['negative_surge']=self.data[surge]*-1.
        self.dfout['positive_tide']=self.data[tide]
        self.dfout['negative_tide']=self.data[tide]*-1.
        folderout=os.path.join(args['folder out'])

        ## Inputs
        surge_mode=args['Surge']
        if surge_mode=='Both (neg and pos)':
            surges=['positive_','negative_']
        elif surge_mode=='Positive only':
            surges=['positive_']
        elif surge_mode=='Negative only':            
            surges=['negative_']


        fitting=args['Fitting distribution']
        method=args['Method']
        min_peak=args['Minimum number of peaks over threshold']
        rv=args['Return period']
        if ~isinstance(rv,np.ndarray):
            rv=np.array(rv)
       

        drr_interval=[0,360]   

        time_blocking=args['Time blocking']
        pks_opt={}
        thresh=args['threshold value']

        if args['threshold type']=='percentile':
            sort_data=np.sort(np.abs(self.dfout[surge].values))
            pks_opt['height']=sort_data[int(np.round(len(sort_data)*(thresh/100)))]
        else:
            pks_opt['height']=thresh

        pks_opt['distance']=args['Minimum time interval between peaks (h)']*(self.sint/3600)
        to_export=[]
        for surge in surges:

            self._get_peaks(surge+'surge',time_blocking=time_blocking,peaks_options=pks_opt,min_peak=min_peak)

            if 'Omni' not in self.peaks_index['Annual']:
                return 'No Peak found !!'
            else:
                self._clean_peak()

            self._do_EVA_water(surge+'surge',surge+'tide',rv,fitting,method,time_blocking,pks_opt['height'])

            if args['Display peaks']=='On':
                self._plot_peaks(surge+'surge',display=True,folder=folderout)
            else:
                self._plot_peaks(surge+'surge',display=False,folder=folderout)

            if args['Display CDFs']=='On':
                self._plot_cdfs(surge+'surge',display=True,folder=folderout)
            else:
                self._plot_cdfs(surge+'surge',display=False,folder=folderout)

            to_export.append(surge+'surge')

        self._export_as_xls(to_export,rv,os.path.join(folderout,'EVA_water.xlsx'))

    def do_extreme(self,magnitude='magnitude',tp_optional='tp_optional',direction_optional='direction_optional',tm_optional='tm_optional',water_depth_optional='water_depth_optional',\
        args={'Fitting distribution':{'Weibull':True,'Gumbel':False,'GPD':False,'GEV':False},
         'Method':{'pkd':False,'pwm':False,'mom':False,'ml':True},
         'Slope fitting distribution':{'Weibull':True,'Gumbel':False},
         'Slope treshold':0.005,
         'Return period':[1,10,25,50,100],
         'Estimate Hmax & Cmax RPVs':{'On':False,'Off':True},
         'threshold type':{'percentile':True,'value':False},
         'threshold value':95.0,
         'Directional':{'On':True,'Off':False},
         'Minimum number of peaks over threshold': 30,
         'Minimum time interval between peaks (h)':24.0,
         'Direction binning':{'centered':True,'not-centered':False},
         'Direction interval': 45.,
         'Time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
         'Display peaks':{'On':True,'Off':False},
         'Display CDFs':{'On':True,'Off':False},
         'Water depth':5000.0,
         'folder out':os.getcwd()
         }):
    

        '''%This function is used for extreme value analysis of any type. It generates
        %return period values for any parameters. Inputs can be:
        %-only magnitude (omni-directional extreme value ananlysis)
        %-magnitute and direction (directional ARI with omni or directional POT)_
        %-wave magnitude and period (omni-directional analysis and bi-variate,
        % Hs vs. Tp, extremes, estimated using the FORM method)
        %-wave magnitude, period and direction (directional ARI with omni or
        % directional POT and bi-variate extremes, Hs vs. Tp, estimated using the
        % FORM method for each selected directions)'''

        # variabl check
        if tp_optional not in self.data:
            tp_optional=None
        if direction_optional not in self.data:
            direction_optional=None
        if tm_optional not in self.data:
            tm_optional=None
        if water_depth_optional not in self.data:
            water_depth_optional=None
            
        folderout=os.path.join(args['folder out'])

        ## Inputs
        slp_fitting=args['Slope fitting distribution']
        slp_threshold=args['Slope treshold']
        fitting=args['Fitting distribution']
        method=args['Method']
        min_peak=args['Minimum number of peaks over threshold']
        rv=args['Return period']
        if ~isinstance(rv,np.ndarray):
            rv=np.array(rv)

        if water_depth_optional in self.data:
            h=np.nanmean(self.data[water_depth_optional])
        else:
            h=args['Water depth']

        Hmax_RPV=True
        if args['Estimate Hmax & Cmax RPVs']=='Off':
            Hmax_RPV=False
        

        if args['Directional']=='On':
            drr_interval=dir_interval(args['Direction interval'],args['Direction binning'])
        else:
            drr_interval=[0,360]

        

        time_blocking=args['Time blocking']
        pks_opt={}
        thresh=args['threshold value']
        if args['threshold type']=='percentile':
            sort_data=np.sort(self.dfout[magnitude].values)
            pks_opt['height']=sort_data[int(np.round(len(sort_data)*(thresh/100)))]
        else:
            pks_opt['height']=thresh

        pks_opt['distance']=args['Minimum time interval between peaks (h)']*(self.sint/3600)

        self._get_peaks(magnitude,drr=direction_optional,directional_interval=drr_interval,time_blocking=time_blocking,peaks_options=pks_opt,min_peak=min_peak)

        if 'Omni' not in self.peaks_index['Annual']:
            return 'No Peak found !!'
        else:
            self._clean_peak()

        if tp_optional in self.data:
            self.dfout['slp']=calc_slp(self.data[magnitude],self.data[tp_optional],h=h)
            self.dfout['slp'].mask(self.dfout['slp']<slp_threshold, inplace=True)

        self._do_EVA(magnitude,tp_optional,tm_optional,rv,fitting,slp_fitting,method,h,Hmax_RPV)

        if args['Display peaks']=='On':
            self._plot_peaks(magnitude,display=True,folder=folderout)
        else:
            self._plot_peaks(magnitude,display=False,folder=folderout)

        if args['Display CDFs']=='On':
            self._plot_cdfs(magnitude,display=True,folder=folderout)
            if tp_optional in self.data: 
               self._plot_contours(magnitude,rv,drr='Omni',display=True,folder=folderout)
        else:
            self._plot_cdfs(magnitude,display=False,folder=folderout)
            if tp_optional in self.data: 
               self._plot_contours(magnitude,rv,drr='Omni',display=False,folder=folderout)
        

        self._export_as_xls([magnitude,'tp','tmin','tmax','hmax','cmax'],rv,filename=os.path.join(folderout,'EVA.xlsx'))

    def _clean_peak(self):
        keys=list(self.peaks_index.keys())
        for key in keys:
            if len(self.peaks_index[key])==0:
                self.peaks_index.pop(key)

    def _do_EVA_water(self,mag,tide,rp,fitting,method,time_blocking,threshold):

        el_res=self.dfout[mag]
        et=self.dfout[tide].values

        number_of_loops,identifiers,month_identifier=get_number_of_loops(time_blocking)
        months=self.dfout.index.month
        idx=np.arange(0,len(months))
        mag_values=self.dfout[mag]
        for j in range(0,number_of_loops):
        #Pull out relevant indices for particular month/months
            if identifiers[j] in self.peaks_index:
                peak= self.peaks_index[identifiers[j]]['Omni']
                index = np.in1d(months, month_identifier[j])
                if identifiers[j] not in self.eva_stats:
                    self.eva_stats[identifiers[j]]={}
                    self.eva_stats[identifiers[j]]['Omni']={}

                if mag not in self.eva_stats[identifiers[j]]['Omni']:
                    self.eva_stats[identifiers[j]]['Omni'][mag]={}

                y=get_mag_for_water_elevation(self.dfout[mag][index].values,self.dfout[tide].values,threshold)
                loc=min(y)-0.01;
                krP=calc_kRp(rp,len(peak),self.nyear,Hmp=False)
                phat,scale,shape=do_fitting(y,fitting,method,loc=loc)
                magex=phat.isf(krP)
                self.eva_stats[identifiers[j]]['Omni'][mag]['phat']=phat
                self.eva_stats[identifiers[j]]['Omni'][mag]['scale']=scale
                self.eva_stats[identifiers[j]]['Omni'][mag]['shape']=shape
                self.eva_stats[identifiers[j]]['Omni'][mag]['magex']=magex



    def _do_EVA_mag(self,mag,peak,rp,fitting,method):
        stat={}
        krP=calc_kRp(rp,len(peak),self.nyear,Hmp=False)
        phat,scale,shape=do_fitting(self.dfout[mag].values[peak],fitting,method)
        magex=phat.isf(krP)
        stat['phat']=phat
        stat['scale']=scale
        stat['shape']=shape
        stat['magex']=magex
        return stat

    def _do_EVA_hstp(self,hs_name,tp_name,peak,rp,fitting,slp_fitting,method,h=-5000):
        '''% correction of the systematic overestimation of extreme Tp in Shallow
        % water associated with the dependence btw hs and steepness (see Thiebaut
        %and McComb 2015, Coasts&Ports conference, Auckland)
        %1st calcualte the moving average slp vs hs'''
        hs=self.dfout[hs_name].values[peak]
        tp=self.dfout[tp_name].values[peak]
        slp=self.dfout['slp'].values[peak]
        gd=~np.isnan(slp)
        hsfilt=hs[gd]
        tpfilt=tp[gd]
        slpfilt=slp[gd]
        

        n=int(min(5,np.round(len(hsfilt)/4)))
        
        tmp=np.linspace(min(hsfilt),max(hsfilt),n+1)
        step=tmp[1]-tmp[0]
        slp_avg=np.ones((n,))*np.NaN

        for i in range(0,n):
            slp_avg[i]=np.nanmean(slpfilt[np.logical_and(hsfilt>=tmp[i],hsfilt <= tmp[i+1])])

        hs_avg=tmp[:-1]+step/2

        #then calcualtes the linear fit to the averaged slp values. Compared to the fit the all slp values, this improves
        #the accuracy of the associated Tp for large Hs values when they are only a few events
        gd=np.logical_and(~np.isnan(hs_avg),~np.isnan(slp_avg))

        C=np.polyfit(hs_avg[gd],slp_avg[gd],1)
        #Y=np.polyval(C,tmp);hold on;plot(int,Y,'r')
        slpfilt=slpfilt-C[0]*hsfilt
        slploc=min(slpfilt)-.001;
        krP=calc_kRp(rp,len(peak),self.nyear,Hmp=False)

        phat,scale,shape=do_fitting(hsfilt,fitting,method)
        hsex=phat.isf(krP)

        phat_slp,scale_slp,shape_slp=do_fitting(slpfilt,slp_fitting,method,loc=slploc)

        krP=calc_kRp(rp,len(peak),self.nyear,Hmp=False)


        hspot=hsfilt.copy()
        tppot=tpfilt.copy()

        #iFORM
        
        beta=norm.ppf(1-krP) #wnorminv(1-kRp);
        theta=np.arange(0,2*np.pi+(np.pi/50),np.pi/50)

        cos_cdf=norm.cdf(np.outer(beta,np.cos(theta)))
        sin_cdf=norm.cdf(np.outer(beta,np.sin(theta)))
        sin0_cdf=norm.cdf(np.outer(beta,np.sin(0)))
        loc=np.nanmin(hsfilt)*.999

        if fitting.lower()=='weibull':
            hsq=ws.weibull_min.ppf(cos_cdf,shape,scale=scale,loc=loc)
        elif fitting.lower()=='gumbel':
            hsq=ws.gumbel_r.ppf(cos_cdf,scale,shape)+loc
        elif fitting.lower()=='gpd':
            hsq=ws.genpareto.ppf(cos_cdf,-shape,scale=scale,loc=loc)
        elif fitting.lower()=='gev':
            hsq=ws.genextreme.ppf(cos_cdf,shape,scale=scale,loc=loc)

        
        if slp_fitting.lower()=='weibull':
            I1=ws.weibull_min.ppf(sin_cdf,shape_slp,scale=scale_slp,loc=slploc)+C[0]*hsq
            I2=(ws.weibull_min.ppf(sin0_cdf,shape_slp,scale=scale_slp,loc=slploc)).T+C[0]*hsex
        elif slp_fitting.lower()=='gumbel':
            I1=ws.gumbel_r.ppf(sin_cdf,shape_slp,scale=scale_slp)+slploc+C[0]*hsq
            I2=(ws.gumbel_r.ppf(sin0_cdf,shape_slp,scale=scale_slp)+slploc).T+C[0]*hsex
                
        #import pdb;pdb.set_trace()
        g=9.81
        if h<0: #deep water
            tpq=np.sqrt(2*np.pi*hsq/(g*I1))
            tpex=np.sqrt(2*np.pi*hsex/(g*I2))
        else:
            Lq=hsq/I1
            tpq=np.sqrt(2*np.pi*Lq/(g*np.tanh(2*np.pi*h/Lq)))
            Lex=hsex/I2
            tpex=np.sqrt(2*np.pi*Lex/(g*np.tanh(2*np.pi*h/Lex)))
 

        Tmin=np.ones((tpq.shape[0],))*np.nan
        Tmax=np.ones((tpq.shape[0],))*np.nan

        if ~np.all(np.isnan(hsex)):  
            for i in range(0,tpq.shape[0]):
                A = PolyArea(np.concatenate((tpq[i,:],[tpq[i,0]])),np.concatenate((hsq[i,:],[hsq[i,0]])))
                if A>0:
                    #find minimum period
                    B = 0
                    n=0
                    while B<0.05*A:
                        ind=(tpq[i,:]<np.nanmin(tpq[i,:])+(n+1)*0.1).nonzero()[0]
                        B=PolyArea(np.concatenate((tpq[i,ind],[tpq[i,ind[0]]])),np.concatenate((hsq[i,ind],[hsq[i,ind[0]]])))
                        n+=1

                    Tmin[i] = np.max(tpq[i,ind])
                    #find mximum period
                    B = 0
                    n= 0

                    while B<0.05*A:
                        ind=(tpq[i,:]>np.nanmax(tpq[i,:])-(n+1)*0.1).nonzero()[0]
                        B=PolyArea(np.concatenate((tpq[i,ind],[tpq[i,ind[0]]])),np.concatenate((hsq[i,ind],[hsq[i,ind[0]]])))
                        n+=1
                    Tmax[i] = np.min(tpq[i,ind])



        stat={}
        stat[hs_name]={}
        stat[hs_name]['magex'] = hsex
        stat[hs_name]['phat'] = phat
        stat[hs_name]['scale'] = scale
        stat[hs_name]['shape'] = shape
        stat[hs_name]['hsq'] = hsq
        stat[hs_name]['hspot'] = hspot

        stat['slp']={}
        stat['slp']['phat'] = phat_slp
        stat['slp']['scale'] = scale_slp
        stat['slp']['shape'] = shape_slp

        stat['tp']={}
        stat['tmin']={}
        stat['tmax']={}
        stat['tmin']['magex'] = Tmin#[:,0]
        stat['tmax']['magex'] = Tmax#[:,0]
        stat['tp']['magex'] = tpex
        stat['tp']['tpq'] = tpq
        stat['tp']['tppot'] = tppot


       # import pdb;pdb.set_trace()
        return stat

        

    def _do_EVA_hmp(self,mag,peak,rp,fitting,method):
        stat={}

        kRp=calc_kRp(rp,len(peak),self.nyear,Hmp=True)
        phat,scale,shape=do_fitting(self.dfout[mag].values[peak],fitting,method)
        LnN=self.dfout['LnN'].values[peak]

        loc=np.nanmin(phat.data)*.999
        x=np.linspace(loc,np.max(phat.data),1000);
        dx=x[1]-x[0]


        if fitting.lower()=='weibull':
            P_lt=ws.weibull_min.pdf(x-loc,shape,scale=scale)
        elif fitting.lower()=='gumbel':
            P_lt=ws.gumbel_r.pdf(x-loc,scale,shape)
        elif fitting.lower()=='gpd':
            P_lt=ws.genpareto.pdf(x-loc,-shape,scale=scale)
        elif fitting.lower()=='gev':
            P_lt=ws.genextreme.pdf(x-loc,shape,scale=scale)

        P_lt[np.isinf(P_lt)]=0
        LnN=np.nanmean(LnN);
        
        #convolution method p.390 of TROMANS and VANDERSCHUREN (1995)
        h=np.linspace(0,30,3001) #;% 0.01 precision
        
        X=repmat(x,len(h),1)
        P_LT=repmat(P_lt,len(h),1)
        H=repmat(h,len(x),1).T
        P=np.exp(-np.exp(-LnN * (((H/X)**2 -1 )) )) * P_LT 
        
        P=np.sum(P,1)*dx
        P=P/np.max(P)
        magex=np.ones((len(kRp),))*np.NaN
        for i in range(0,len(kRp)):
            P_poisson_process=P**kRp[i] #% p.390 of TROMANS and VANDERSCHUREN (1995)
            id_last=(P_poisson_process<1/np.exp(1)).nonzero()[0]
            hh=[]
            if len(id_last)>0:
                hh.append(h[id_last[-1]])

            id_first=(P_poisson_process>1/np.exp(1)).nonzero()[0]
            if len(id_first)>0:
                hh.append(h[id_first[0]])

            magex[i]=np.mean(hh)


        stat['phat']=phat
        stat['scale']=scale
        stat['shape']=shape
        stat['magex']=magex
        return stat

    def _do_EVA(self,mag,tp,tm,rp,fitting,slpfit,method,h,Hmax_RPV):
        months=self.peaks_index.keys()
        for month in months:
            self.eva_stats[month]={}
            drrs=self.peaks_index[month].keys()
            for d in drrs:
                peak=self.peaks_index[month][d]
                self.eva_stats[month][d]={}
                if 'slp' in self.dfout:
                    self.eva_stats[month][d]=self. _do_EVA_hstp(mag,tp,peak,rp,fitting,slpfit,method,h)
                else:
                    self.eva_stats[month][d][mag]=self._do_EVA_mag(mag,peak,rp,fitting,method)
                
                if Hmax_RPV:
                    ind=self.peaks_index[month][d]
                    self._calc_Hmp(mag,ind,tm=tm,depth=h,max_storm_duration=48)
                    self.eva_stats[month][d]['hmax']=self._do_EVA_hmp('Hmp',peak,rp,fitting,method)
                    self.eva_stats[month][d]['cmax']=self._do_EVA_hmp('Cmp',peak,rp,fitting,method)


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
        
    def _plot_contours(self,mag,rp,drr='Omni',display=False,folder=os.getcwd()):


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


            tpq=self.eva_stats[months[j]][drr]['tp']['tpq']
            hsq=self.eva_stats[months[j]][drr][mag]['hsq']
            hsex=self.eva_stats[months[j]][drr][mag]['magex']
            tpex=self.eva_stats[months[j]][drr]['tp']['magex']
            tppot=self.eva_stats[months[j]][drr]['tp']['tppot']
            hspot=self.eva_stats[months[j]][drr][mag]['hspot']

            hsv = cm = plt.get_cmap('hsv') 
            cNorm  = colors.Normalize(vmin=0, vmax=tpq.shape[0])
            scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=hsv)

            for i in range (0,tpq.shape[0]):
                x=np.concatenate((tpq[i,:],[tpq[i,0]]))
                y=np.concatenate((hsq[i,:],[hsq[i,0]]))
                ax.plot(x,y,label=rp[i],color = scalarMap.to_rgba(i))

            ax.set_xlabel('Tp (s)')
            ax.set_ylabel('Hs (m)')
            
            ax.plot(tppot,hspot,'.')
            ax.set_xlim([np.nanmin(tpq)-.5,min(np.nanmax(tpq)+.5, 45)])
            ax.set_ylim([np.nanmin(hsq)-.2,np.nanmax(hsq)+.2])
            ax.plot(tpex[0,:],hsex,'kx')
            ax.set_title(months[j])
            if j==number_of_loops-1:
               ax.legend(loc='best')  

        
        fig.align_labels()
        # if number_of_loops>10:
        #     plt.subplots_adjust(left=0.075,right=0.970,bottom=0.1,top=0.97,hspace=.5,wspace=0.415)            
        # elif number_of_loops>2 and number_of_loops<10:
        #     plt.subplots_adjust(left=0.08,right=0.975,bottom=0.1,top=0.7,hspace=.5,wspace=0.3)
        # else:
        #     plt.subplots_adjust(bottom=0.05,top=.95,hspace=.5)
      
        if display:
            plt.show(block=~display)

        plt.savefig(os.path.join(folder,'RPV_FORM_'+mag+'_'+drr+'.png'))
        #plt.close()

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
            ax = plt.subplot(sub)
            stat=self.eva_stats[months[j]][drr][mag]
            ws.probplot(stat['phat'].data, stat['phat'].par, dist=stat['phat'].dist.name, plot=ax)
            ax.set_title(months[j])


        fig.align_labels()
        # if number_of_loops>10:
        #     plt.subplots_adjust(left=0.075,right=0.970,bottom=0.1,top=0.97,hspace=.5,wspace=0.415)            
        # elif number_of_loops>2 and number_of_loops<10:
        #     plt.subplots_adjust(left=0.08,right=0.975,bottom=0.1,top=0.7,hspace=.5,wspace=0.3)
        # else:
        #     plt.subplots_adjust(bottom=0.05,top=.95,hspace=.5)
      
        if display:
            plt.show(block=False)

        plt.savefig(os.path.join(folder,'cdf_'+mag+'_'+drr+'.png'))


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
      
       
        plt.savefig(os.path.join(folder,mag+'_peaks.png'))
        if display:
            plt.show(block=~display)
        else:
            plt.close()

    def _calc_Hmp(self,hs,ind,tm=None,depth=5000,max_storm_duration=48):

        '''#Estimates the most probable maximum wave heights Hmp and maximum crest Cmp of storms with peak
        #significant wave heights hs(ind) using the Rayleigh and Weibull distributions and the
        #method described in TROMANS and VANDERSCHUREN (1995, page 389).
        #Methods complying with ISO (2005)
        #Inputs:
        # hs: significant wave height time series (in m)
        # ind: indices of storm peaks
        # tm: mean wave period time series (in s)
        # depth: water depth in m
        # max_storm_duration: arbitrary maximum storm duration (in h).
        # sint: time interval (in h).
        #Outputs:
        # Hmp: most probable maximum wave height for each storm (in m)
        # Cmp: most probable maximum crest for each storm (in m)
        # LnN = log(Ts/tm) where Ts is the time scale of the storm (in s) (see  TROMANS and VANDERSCHUREN (1995, eqs. 1-2))'''
        self.dfout['Hmp']=np.NaN
        self.dfout['Cmp']=np.NaN
        self.dfout['LnN']=np.NaN
        
        hs=self.dfout[hs].values

        # from scipy.io import savemat
        # mdic = {"hs": hs, "ind": ind}
        # savemat("matlab_matrix.mat", mdic)

        mx=int(np.round(max_storm_duration/(self.sint/3600)*.5))#half of arbitray maximum storm duration
        no_storm=.6 #;#arbitrary assumption: no storm condition below 60# of the peak value
        x=np.linspace(0,30,600);

        g=9.81;


        if (tm is not None) and (tm in self.dfout):
            tm=self.dfout[tm].values
        else:
            tm=np.ones((len(hs),))

        for i in range(0,len(ind)):
    

            storm_start=max((hs[0:ind[i]]<no_storm*hs[ind[i]]).nonzero()[0][-1],ind[i]-mx)
            storm_start=max(int(storm_start),1)
            storm_end=min(ind[i]-1+(hs[ind[i]:]<no_storm*hs[ind[i]]).nonzero()[0][0],ind[i]+mx)
            
            storm_end=min(int(storm_end),len(hs))
            
            index=np.arange(storm_start,storm_end)
            st=(~np.isnan(hs[index])).nonzero()[0][0]
            en=(~np.isnan(hs[index])).nonzero()[0][-1]
            index=index[st:en+1]
            
            #

            hs_storm=hs[index]
            nQ=np.empty((len(x),len(hs_storm)))*np.NaN
            nQc=np.empty((len(x),len(hs_storm)))*np.NaN
            tm_storm = tm[index]
            if np.all(tm_storm==1):
                tm_storm = 10.8*tm_storm
                n=1000*tm*(self.sint/3600)/3
            else:               
                n=3600*self.sint/tm_storm;#number of waves in 3 hours

            
            for j in range(0,len(hs_storm)):
                # #max wave height distribution (Rayleigh)
                # nQ(:,j)=n(j)*(exp(-2*(x./hs_storm(j)).^2));
                #max wave height distribution (Forristal, 1978; ISO, 2015 eq. A.35)
                
                nQ[:,j]=n[j]*np.exp(-(4*x/hs_storm[j])**2.126/8.42)
                #max crest distribution (Weibull) (suggested by Forristal 2000, p. 1942)
                S1=2*np.pi*hs_storm[j]/(g*tm_storm[j]**2);#wave steepness
                Ur=hs_storm[j]/(wavenuma(2*np.pi/tm_storm[j],depth)*depth**3)#Ursell Number
                alpha=0.3536 + 0.2568*S1 + 0.0800*Ur
                beta= 2-1.7912*S1 - 0.5302*Ur +0.284*Ur**2
                nQc[:,j]=n[j]*(np.exp(-(x/(alpha*hs_storm[j]))**beta))
            
            
            Prob_max=np.exp(-np.nansum(nQ,1))#TROMANS and VANDERSCHUREN (1995, page 389, paragraph "the probability distribution of the extreme wave of a given storm history")
            Prob_maxc=np.exp(-np.nansum(nQc,1))#TROMANS and VANDERSCHUREN (1995, page 389,paragraph "the probability distribution of the extreme wave of a given storm history")
            self.dfout['Hmp'][ind[i]]=(x[(Prob_max<1/np.exp(1)).nonzero()[0][-1]]+x[(Prob_max>1/np.exp(1)).nonzero()[0][0]])/2.#TROMANS and VANDERSCHUREN (1995, page 389, paragraph "the "short time" variability")
            self.dfout['Cmp'][ind[i]]=(x[(Prob_maxc<1/np.exp(1)).nonzero()[0][-1]]+x[(Prob_maxc>1/np.exp(1)).nonzero()[0][0]])/2.#TROMANS and VANDERSCHUREN (1995, page 389, paragraph "the "short time" variability)
            self.dfout['LnN'][ind[i]]=np.log(len(index)*self.sint/np.nanmean(tm_storm))#TROMANS and VANDERSCHUREN (1995, page 388)
        

        
        #References:

        #Forristall, G.Z., 1978. On the statistical distribution of wave heights 
        #in a storm. J. Geophys. Res. Oceans 83, 2353�2358.

        #TROMANS, P. S. and VANDERSCHUREN, L., Response based design
        #conditions in the North Sea: application of a new method. Proc. 27th
        #Offshore Technology Conference, paper OTC 7683, Houston, May 1995.

        #Forristall, G. Z., 2000: Wave Crest Distributions: Observations and
        #Second-Order Theory. J. Phys. Oceanogr., 30, 1931�1943.

        #ISO (2005). BS EN ISO 19901-1:2005, Petroleum and Natural Gas Industries
        #�Specific Requirements for Offshore Structures � Part 1: Metocean Design
        #and Operating Conditions British Standards Institute.

        #ISO, 2015. 19901-1:2015(en) Petroleum and natural gas industries - 
        #Specific requirements for offshore structures - Part 1: Metocean design 
        #and operating conditions. Br. Stand. Inst.



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
                        index2=(drr_values>directional_interval[jj]) | (drr_values<=directional_interval[jj+1])
                    else:
                        index2=(drr_values>directional_interval[jj]) & (drr_values<=directional_interval[jj+1])
                index=np.logical_and(index1,index2)
                if np.any(index):
                    tmp=mag_values.values.copy()
                    tmp[~index]=0
                    pk_idx=find_peaks(tmp,**peaks_options)[0]
                    if len(pk_idx)>min_peak:
                        self.peaks_index[identifiers[j]][dir_label]=pk_idx
