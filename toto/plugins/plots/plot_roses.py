import pandas as pd
import os
from ._do_roses import do_roses
from ._do_bias_hist import do_bias_hist
from ._do_density_diagramm import do_density_diagramm
from ._do_qq_plot import qq_plot
from ._do_perc_of_occurence import do_perc_of_occurence
from toto.plugins.statistics._do_joint_prob import _do_joint_prob_plot
from ...core.toolbox import get_opt,dir_interval,get_increment
import numpy as np


@pd.api.extensions.register_dataframe_accessor("StatPlots")
class StatPlots:
    def __init__(self, pandas_obj):
#        self._validate(pandas_obj)
        self.data = pandas_obj
        self.dfout = pd.DataFrame(index=self.data.index.copy())

    def plot_roses(self,mag='mag',drr='drr',\
        args={'Title':'Current speed',\
        'units':'m/s',\
        'Speed bins (optional)':[],
        '% quadran (optional)':[],
        'Time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
        'folder out':os.getcwd(),
        'display':{'On':True,'Off':False}
        }):

        '''% This function provides annual, seasonal or monthly rose plots for wind,
        % wave, current or any direcional variable'''
        display=True
        if args['display']=='Off':
            display=False
        unit=get_opt(self.data[mag],'units',args['units'])
        
        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'_rose.png')
        do_roses(self.data.index,self.data[mag],self.data[drr],unit,args['Title'],
            args['Speed bins (optional)'],args['% quadran (optional)'],args['Time blocking'],filename,display)



    
    def BIAS_histogramm(self,measured='measured',modelled='modelled',
        args={'Nb of bins':30,'Xlabel':'','units':'','display':{'On':True,'Off':False},'folder out':os.getcwd()}):
        display=True
        if args['display']=='Off':
            display=False        
        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'_biasHist.png')
        unit=get_opt(self.data[measured],'units',args['units'])

        short_name=get_opt(self.data[measured],'short_name',args['Xlabel'])

        do_bias_hist(self.data[measured].values,self.data[modelled].values,unit,short_name,args['Nb of bins'],filename,display)


    def density_diagramm(self,X='X',Y='Y',args={
        'Y name':'',
        'X name':'',
        'Y unit':'',
        'X unit':'',
        'X limits':[0,np.inf],
        'Y limits':[0,np.inf],
        'display':{'On':True,'Off':False},
        'folder out':os.getcwd()}):


        ''' This function provides density diagrams of parameter Y vs parameter X,
        % i.e. similar to scatter plot but emphasing on region withg large number
        % of data'''
        display=True
        if args['display']=='Off':
            display=False
        X_short_name=get_opt(self.data[X],'short_name',args['X name'])
        Y_short_name=get_opt(self.data[Y],'short_name',args['Y name'])

        X_unit=get_opt(self.data[X],'units',args['X unit'])
        Y_unit=get_opt(self.data[Y],'units',args['Y unit'])        

        Xlim=args['X limits']
        Ylim=args['Y limits']

        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'_density_diagramm.png')

        do_density_diagramm(self.data[X].values,self.data[Y].values,X_short_name,Y_short_name,X_unit,Y_unit,Xlim,Ylim,display)


    def QQ_plot(self,measured='measured',modelled='modelled',args={
        'measured name':'',
        'modelled name':'',
        'measured unit':'',
        'modelled unit':'',
        'Quantile increment step (%)':1.0,
        'display':{'On':True,'Off':False},
        'folder out':os.getcwd()}):


        ''' % This function provides Quantile-Quantile plots (Q-Q plots) for comparison
        % statistics'''
        display=True
        if args['display']=='Off':
            display=False
        X_short_name=get_opt(self.data[measured],'short_name',args['measured name'])
        Y_short_name=get_opt(self.data[modelled],'short_name',args['modelled name'])

        X_unit=get_opt(self.data[measured],'units',args['measured unit'])
        Y_unit=get_opt(self.data[modelled],'units',args['modelled unit'])        

        pvec=np.arange(0,100+args['Quantile increment step (%)'],args['Quantile increment step (%)'])

        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'_qqplot.png')

        qq_plot(self.data[measured],self.data[modelled],pvec,X_short_name,Y_short_name,X_unit,Y_unit,filename,display)



    def Percentage_of_occurence(self,mag='mag',drr='drr',args={
                'Magnitude interval (optional)':[],
                'X label':'Wind speed in [m/s]',
                'Time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
                'Direction binning':{'centered':True,'not-centered':False},
                'Direction interval': 45.,
                'display':{'On':True,'Off':False},
                'folder out':os.getcwd()}):
        
        display=True
        if args['display']=='Off':
            display=False

        if drr in self.data:
            drr=self.data[drr].values
        else:
            drr=None

        mag_inteval=args['Magnitude interval (optional)']
        X_unit=get_opt(self.data[mag],'units','')
        X_short_name=get_opt(self.data[mag],'short_name','')
        if X_short_name=='':
            xlabel=args['X label']
        else:
            xlabel=X_short_name+' ['+X_unit+']'

        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'_OccurencePlot.png')

        drr_interval=dir_interval(args['Direction interval'],args['Direction binning'])
        do_perc_of_occurence(self.data.index,self.data[mag].values,drr,mag_inteval,xlabel,args['Time blocking'],drr_interval,filename,display)





    def joint_probability_plot(self,X='X',Y='Y',\
        args={    
        'X Min Res Max(optional)':[2,1,22],
        'Y Min Res Max(optional)':[0,0.5],
        'X label':'',
        'Y label':'',
        'Time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
        'Probablity expressed in':{'percent':False,'per thoushand':True},
        'display':{'On':True,'Off':False},
        'folder out':os.getcwd(),
        }):
        ''' This function provides joint distribution graph for X and Y, i.e. the
            probability of events defined in terms of both X and Y (per 1000)
            '''
        display=True
        if args['display']=='Off':
            display=False
        Ydata=self.data[Y]
        Xdata=self.data[X]

        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'JP_wave_nrj.png')

        if args['Probablity expressed in']=='percent':
            multiplier=100.
        else:
            multiplier=1000.
        Y_interval=get_increment(Ydata,args['Y Min Res Max(optional)'])
        X_interval=get_increment(Xdata,args['X Min Res Max(optional)'])      

        X_unit=get_opt(self.data[X],'units','')
        X_short_name=get_opt(self.data[X],'short_name','')
        if X_short_name=='':
            xlabel=args['X label']
        else:
            xlabel=X_short_name+' ['+X_unit+']'

        Y_unit=get_opt(self.data[Y],'units','')
        Y_short_name=get_opt(self.data[Y],'short_name','')
        if Y_short_name=='':
            ylabel=args['Y label']
        else:
            ylabel=Y_short_name+' ['+Y_unit+']'

        _do_joint_prob_plot(filename,self.data.index,Xdata,Ydata,X_interval,Y_interval,args['Time blocking'],display,xlabel,ylabel,multiplier)
