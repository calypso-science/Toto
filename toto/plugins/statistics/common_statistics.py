import pandas as pd
from ...core.toolbox import dir_interval,get_increment
import os
from ._do_comp_stats import do_comp_stats
from ._do_joint_prob import do_joint_prob
from ._do_stats import do_stats
from ._do_stats2 import do_modal_stat,do_weighted_direction
from ._do_exc_stats import do_exc_stats,do_exc_coinc_stats,do_window_stats
from ._do_workability import do_workability
from ._do_wave_pop import do_wave_pop
from ._do_dir_max import do_directional_stat

import numpy as np

@pd.api.extensions.register_dataframe_accessor("Statistics")
class Statistics:
    def __init__(self, pandas_obj):
#        self._validate(pandas_obj)
        self.data = pandas_obj
        self.dfout = pd.DataFrame(index=self.data.index.copy())


    def common_statistics(self,mag=['mag'],drr='drr',args={'Minimum occurrence (main direction) [%]':15,'folder out':os.getcwd(),
        'Time blocking':{'Yearly':True,
        'South hemisphere(Summer/Winter)':False,
        'South hemisphere 4 seasons':False,
        'North hemishere(Summer/Winter)':False,
        'North hemisphere 4 seasons':False,        
        'North hemisphere moosoon(SW,NE,Hot season)':False},
                                                            }):
        """ output stats from timesereis)"""

        if drr not in self.data:
            drr='none'
        else:
            drr=self.data[drr]

        min_occ=args['Minimum occurrence (main direction) [%]']

        if isinstance(drr,str):
            #statf=['min','max','mean','std',[90,95,99]]
            statf=['min','max','mean','std',[1,5,10,50,90,95,99]] 
        else:
            statf=['min','max','mean','std',[1,5,10,50,90,95,99],np.nan]         

        hem=args['Time blocking']
        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'stat.xlsx')
        time=self.data.index

        if isinstance(mag,str):
            mag=[mag]

        for ma in mag:
            data=self.data[ma]
            do_stats(time,statf,data,drr,hem,filename,ma,min_occ)
    
    def comparison_statistics(self,measured='measured',hindcast='hindcast',args={'folder out':os.getcwd()}):
        '''function to output comparison stat between measured and predicted data
            i.e BIAS,MAE,RMSE,MRAE'''

            
        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'compstat.xlsx')
        hind=self.data[hindcast].values
        meas=self.data[measured].values

        
        error_message=do_comp_stats(filename,hind,meas,self.data[hindcast].short_name)
        if isintance(error_message,str):
            return error_message


    def Directional_statistics(self,magnitude='magnitude',direction='direction',\
        args={
        'function':{'Max':True, 'Mean':False, 'Median':False, 'Min':False, 'Percentile':False, 'Prod':False, 'Quantile':False, 'Std':False, 'Sum':False, 'Var':False},
        'Percentile or Quantile': 0.1,
        'folder out':os.getcwd(),
        'Direction binning':{'centered':True,'not-centered':False},
        'Direction interval': 45.,
        'Time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
        }):

        """This function extract stats for each directional bins"""
 

        Ydata=self.data[magnitude]
        Xdata=self.data[direction]

        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'directional_max.xlsx')

        X_interval=dir_interval(args['Direction interval'],args['Direction binning'])
        funct=getattr(np,'nan'+args['function'].lower())
        val=args['Percentile or Quantile']
        if hasattr(self.data[magnitude],'short_name'):
            short_name=self.data[magnitude].short_name
        else:
            short_name=magnitude
        do_directional_stat(filename,funct,val,short_name,self.data.index,Xdata,Ydata,X_interval,args['Time blocking'],args['Direction binning'])


    def joint_probability(self,speed='speed',direction='direction',period='period',\
        args={'method':{'Mag vs Dir':True,'Per Vs Dir':False,'Mag vs Per':False},\
        'folder out':os.getcwd(),
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
            Ydata=self.data[speed]
            Xdata=self.data[period]

        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'JP.xlsx')

        if args['Probablity expressed in']=='percent':
            multiplier=100.
        else:
            multiplier=1000.
        Y_interval=get_increment(Ydata,args['Y Min Res Max(optional)'])
        

        if analysis_method=='Mag vs Dir' or analysis_method=='Per Vs Dir':
            X_interval=dir_interval(args['Direction interval'],args['Direction binning'])
            binning=args['Direction binning']
        else:
            X_interval=get_increment(Xdata,args['X Min Res Max(optional)'])
            binning=''
        

        X_interval=np.append(X_interval,np.nan)
        Y_interval=np.append(Y_interval,np.nan)
        do_joint_prob(filename,self.data.index,Xdata,Ydata,X_interval,Y_interval,args['Time blocking'],binning,multiplier,speed)



    def weather_window(self,data='data',\
        args={'method':{'persistence exceedence':False,'persistence non-exceedence':True},\
        'folder out':os.getcwd(),
        'Exceedance bins: Min Res Max(optional)':[2,1,22],
        'Duration Min Res Max':[6,6,72],
        'Time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
         }):
        """This function calculates the averaged number of full windows for data
            -exceeding specific values during a specific duration (persistence exceedence)
            -non-exceeding specific values during a specific duration (persistence non-exceedence)
            Note: if a window overlaps to the next month/season/year, it is assumed to belong to the
            month/season/year when the window starts."""

        analysis=args['method'] 
        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'_WeatherWindow.xlsx')
        Ydata=self.data[data]
        Exc=get_increment(Ydata,args['Exceedance bins: Min Res Max(optional)'])
        duration=get_increment(Ydata,args['Duration Min Res Max'])
        do_window_stats(filename,self.data.index,Ydata,args['Time blocking'],analysis,Exc,duration)

    def exceedence_probability(self,data='data',\
        args={'method':{'persistence exceedence':True,'persistence non-exceedence':False,\
        'exceedence':False,'non-exceedence':False},\
        'folder out':os.getcwd(),
        'Exceedance bins: Min Res Max(optional)':[2,1,22],
        'Duration Min Res Max':[6,6,72],
        'Time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
         }):
        '''This function calculates the frequency of occurrence of data:
            -exceeding specific values (exceedence)
            -non-exceeding specific values (non-exceedence)
            -exceeding specific values during a specific duration (persistence exceedence)
            -non-exceeding specific values during a specific duration (persistence non-exceedence)'''

        analysis=args['method'] 
        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'_'+analysis.replace(' ','_').replace('-','')+'_stat.xlsx')
        Ydata=self.data[data]
        Exc=get_increment(Ydata,args['Exceedance bins: Min Res Max(optional)'])
        duration=get_increment(Ydata,args['Duration Min Res Max'])
        do_exc_stats(filename,self.data.index,Ydata,args['Time blocking'],analysis,Exc,duration,data)


    def excedence_coincidence_probability(self,data='data',coincident_nodir='coincident_nodir',coincident_with_dir='coincident_with_dir',\
        args={'method':{'exceedence':True,'non-exceedence':False},\
        'folder out':os.getcwd(),
        'Exceedance bins: Min Res Max(optional)':[0,2],
        'Coincidence bins: Min Res Max(optional)':[0,2],
        'Duration Min Res Max':[6,6,72],
        'Direction binning':{'centered':True,'not-centered':False},
        'Direction interval': 45.,
        'Time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
         }):

        '''Exceedence and non-exceedence analysis co-incident with another
            parameter, similar to Joint-probability function but includes a
            cumulative sum to obtain exceedence or non-exceedence(in %).'''

        analysis=args['method'] 
        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'_ExCoincstat.xlsx')
        Y=self.data[data]
        Exc=get_increment(Y,args['Exceedance bins: Min Res Max(optional)'])
        if coincident_nodir=='none':
            analysis_method='Mag_Dir'
            X=self.data[coincident_with_dir]
            X_interval=dir_interval(args['Direction interval'],args['Direction binning'])
            binning=args['Direction binning']
        else:
            analysis_method='Mag_Var'
            X=self.data[coincident_nodir]
            X_interval=get_increment(Y,args['Coincidence bins: Min Res Max(optional)'])
            binning=''
            

        do_exc_coinc_stats(filename,self.data.index,X,Y,Exc,X_interval,args['Time blocking'],analysis_method,analysis,binning)


    def workability(self,data1='data1',data2='data2',data3_optional='data3_optional',data4_optional='data4_optional',\
        args={'method':{'persistence exceedence':True,'persistence non-exceedence':False},\
               'folder out':os.getcwd(),
               'Threshold for each dataset:':[1,10], 
               'Duration Min Res Max':[6,6,72], 
               'Time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
        }):

        '''This function provides workability persistence (non-)exceedence tables, 
            i.e. the % of workable time based on 2 to 4 limiting
            paramters (e.g. Hs < 2m and Wind speed < 10 m/s)'''


        analysis=args['method'] 
        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'_Workability.xlsx')
        duration=get_increment(self.data[data1],args['Duration Min Res Max'])
        Exc=args['Threshold for each dataset:']
        
        variables=[data1,data2]
        if data3_optional in self.data:
            variables.append(data3_optional)
            if data4_optional in self.data:
                variables.append(data4_optional)

        if len(variables)!=len(Exc):
            return 'The number of thresholds differs from the number of selected parameters'


        do_workability(filename,self.data[variables],Exc,duration,args['Time blocking'],analysis)


    def wave_population(self,Hs='Hs',Tm02='Tm02',Drr_optional='Drr_optional',Tp_optional='Tp_optional',SW_optional='SW',\
            args={'Method':{'Height only':True,'Height/Direction':False,'Height/Tp':False,'Height/period':False},
                'Direction binning':{'centered':True,'not-centered':False},
                'Direction interval': 45.,
                'Heigh bin size': 0.5,
                'Period bin size': 2,
                'Exposure (years) (= length of time series if not specified)':0,
                'folder out':os.getcwd(),
                'Directional switch':{'On':True,'Off':False}
            }):


        ''' This function computes the wave population for fatigue analysis
            - Based on Rayleigh distribution if spectral width parameter (SW) is not
              specified.
            - Based on Longuet-Higgins Hs-Tp joint probability distribution if SW is
              specified'''

        if args['Directional switch']=='On':
            drr_switch=True
        else:
            drr_switch=False
        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'_Wavepop.xlsx')
        method=args['Method']
        Ddir=dir_interval(args['Direction interval'],args['Direction binning'])
        if Tp_optional not in self.data:
            Tp=None
        else:
            Tp=self.data[Tp_optional].values

        if SW_optional not in self.data:
            Sw=None
        else:
            Sw=self.data[SW_optional].values

        if Drr_optional not in self.data:
            Drr=None
        else:
            Drr=self.data[Drr_optional].values


        do_wave_pop(self.data.index,self.data[Hs].values,self.data[Tm02].values,Drr,\
            Tp,Sw,method,args['Heigh bin size'],Ddir,args['Period bin size'],\
            args['Exposure (years) (= length of time series if not specified)'],drr_switch,filename)

    

        
    def modal_wave_period(self,Hs='Hs',Tp='Tp',args={'folder out':os.getcwd(),
                                                    'type':{'South hemisphere(Summer/Winter)':True,\
                                                            'South hemisphere 4 seasons': False,
                                                            'North hemishere(Summer/Winter)':False,
                                                            'North hemisphere moosoon(SW,NE,Hot season)':False,
                                                            'North hemisphere 4 seasons': False
                                                            }}):

    
        ''' This function computes the modal period for a set of hs/tp
            The modal period is taken as the mean period of the top 5% of wave height'''
        hem=args['type']
        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'modal_wave_period.xlsx')
        hs=self.data[Hs]
        tp=self.data[Tp];
        time=self.data.index
        do_modal_stat(time,hs,tp,hem,filename)     

    def weighted_direction(self,Hs='Hs',drr='drr',args={'folder out':os.getcwd(),
                                                    'type':{'South hemisphere(Summer/Winter)':True,\
                                                            'South hemisphere 4 seasons': False,
                                                            'North hemishere(Summer/Winter)':False,
                                                            'North hemisphere moosoon(SW,NE,Hot season)':False,
                                                            'North hemisphere 4 seasons': False
                                                            }}):

    
        '''This function computes the energy weighted-dreiction based on 
            input timeseries of Hs and Dir'''

        hem=args['type']
        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'weighted_direction.xlsx')
        hs=self.data[Hs]
        drr=self.data[drr];
        time=self.data.index
        do_weighted_direction(time,hs,drr,hem,filename)   