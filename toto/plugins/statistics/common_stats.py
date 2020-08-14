import pandas as pd
from ...core.toolbox import dir_interval,get_increment
import os
from ._do_comp_stats import do_comp_stats
from ._do_joint_prob import do_joint_prob
from ._do_stats import do_stats
from ._do_exc_stats import do_exc_stats,do_exc_coinc_stats
import numpy as np

@pd.api.extensions.register_dataframe_accessor("Statistics")
class Statistics:
    def __init__(self, pandas_obj):
#        self._validate(pandas_obj)
        self.data = pandas_obj
        self.dfout = pd.DataFrame(index=self.data.index.copy())


    def common_stats(self,mag='mag',drr='drr',args={'folder out':'/tmp/',
                                                    'type':{'South hemisphere(Summer/Winter)':True,\
                                                            'South hemisphere 4 seasons': False,
                                                            'North hemishere(Summer/Winter)':False,
                                                            'North hemisphere moosoon(SW,NE,Hot season)':False,
                                                            'North hemisphere 4 seasons': False
                                                            }}):


        if drr not in self.data:
            drr='none'
        else:
            drr=self.data[drr]

        if isinstance(drr,str):
            statf=['min','max','mean','std',[1,5,10,50,80,90,95,98,99]]
        else:
            statf=['min','max','mean','std',[1,5,10,50,80,90,95,98,99],np.nan]         

        hem=args['type']
        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'stat.xlsx')
        sheetname=self.data[mag].short_name
        data=self.data[mag];
        time=self.data.index
        do_stats(time,statf,data,drr,hem,filename,sheetname)

    def joint_prob(self,speed='speed',direction='direction',period='period',\
        args={'method':{'Mag vs Dir':True,'Per Vs Dir':False,'Mag vs Per':False},\
        'folder out':'/tmp/',
        'X Min Res Max(optional)':[2,1,22],
        'Y Min Res Max(optional)':[0,0.5],
        'Direction binning':{'centered':True,'not-centered':False},
        'Direction interval': 45.,
        'Time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
        'Probablity expressed in':{'percent':False,'per thoushand':True}
        }):
        ''' This function provides joint distribution tables for X and Y, i.e. the
            probability of events defined in terms of both X and Y (per 1000)
            It can be applied for magnitude-direction, magnitude-period or
            period-direction'''

        analysis_method=args['method']

        if analysis_method=='Mag vs Dir':
            Ydata=self.data[speed]
            Xdata=self.data[direction]

        elif analysis_method=='Per Vs Dir':
            Ydata=self.data[period]
            Xdata=self.data[direction]
        elif analysis_method=='Mag vs Per':
            Ydata=self.data[magnitude]
            Xdata=self.data[period]

        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'JP.xlsx')

        if args['Probablity expressed in']=='percent':
            multiplier=100.
        else:
            multiplier=1000.
        Y_interval=get_increment(Ydata,args['Y Min Res Max(optional)'])
        

        if analysis_method=='Mag vs Dir' or analysis_method=='Per Vs Dir':
            X_interval=dir_interval(args['Direction interval'],args['Direction binning'])
        else:
            X_interval=get_increment(Xdata,ags['X Min Res Max(optional)'])
        

        X_interval=np.append(X_interval,np.nan)
        Y_interval=np.append(Y_interval,np.nan)
        do_joint_prob(filename,self.data.index,Xdata,Ydata,X_interval,Y_interval,args['Time blocking'],args['Direction binning'],multiplier)


    def comparison_stats(self,measured='measured',hindcast='hindcast',args={'folder out':'/tmp/'}):
        '''function out=comparison_stat(varargin)
                        % % Input:
                        % %     Hindcast data
                        % %     Measured data
                        % %     Output:
                        % % Function:
                        % %     Do a comparison btw hindcast data and measured dta
                        % % Output: 
                        % %     MAE
                        % %     RMSE
                        % %     MRAE
                        % %     BIAS'''

            
        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'compstat.xlsx')
        hind=self.data[hindcast].values
        meas=self.data[measured].values

        
        error_message=do_comp_stats(filename,hind,meas,self.data[hindcast].short_name)
        if isintance(error_message,str):
            return error_message

    def exc_prob(self,data='data',\
        args={'method':{'persistence exceedence':True,'persistence non-exceedence':False,\
        'exceedence':False,'non-exceedence':False},\
        'folder out':'/tmp/',
        'Exceedance bins: Min Res Max(optional)':[2,1,22],
        'Duration Min Res Max':[6,6,72],
        'Time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
         }):
        '''%This function calculates the frequency of occurrence of data:
        %-exceeding specific values (exceedence)
        %-non-exceeding specific values (non-exceedence)
        %-exceeding specific values during a specific duration (persistence exceedence)
        %-non-exceeding specific values during a specific duration (persistence non-exceedence)'''

        analysis=args['method'] 
        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'_Excstat.xlsx')
        Ydata=self.data[data]
        Exc=get_increment(Ydata,args['Exceedance bins: Min Res Max(optional)'])
        duration=get_increment(Ydata,args['Duration Min Res Max'])
        do_exc_stats(filename,self.data.index,Ydata,args['Time blocking'],analysis,Exc,duration)


    def exc_coinc_prob(self,data='data',coincident_nodir='coincident_nodir',coincident_with_dir='coincident_with_dir',\
        args={'method':{'exceedence':False,'non-exceedence':False},\
        'folder out':'/tmp/',
        'Exceedance bins: Min Res Max(optional)':[0,2],
        'Coincidence bins: Min Res Max(optional)':[0,2],
        'Duration Min Res Max':[6,6,72],
        'Direction binning':{'centered':True,'not-centered':False},
        'Direction interval': 45.,
        'Time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
         }):
        '''% Exceedence and non-exceedence analysis co-incident with another
        % parameter, similar to Joint-probability function but includes a
        % cumulative sum to obtain exceedence or non-exceedence(in %).'''
        analysis=args['method'] 
        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'_ExCoincstat.xlsx')
        X=self.data[data]
        Exc=get_increment(X,args['Exceedance bins: Min Res Max(optional)'])
        if coincident_nodir=='none':
            analysis_method='Mag_Dir'
            Y=self.data[coincident_with_dir]
            Y_interval=dir_interval(args['Direction interval'],args['Direction binning'])
        else:
            analysis_method='Mag_Var'
            Y=self.data[coincident_nodir]
            Y_interval=get_increment(Y,args['Coincidence bins: Min Res Max(optional)'])

            

        do_exc_coinc_stats(filename,self.data.index,X,Y,Exc,Y_interval,args['Time blocking'],analysis_method,analysis,args['Direction binning'])

