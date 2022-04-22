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



# def clean_args(args):
#     for key in args:
#         if isinstance(args[key],dict):
#             for subkey in args[key]:
#                 if args[key][subkey]:
#                     args[key]=subkey
#                     break


@pd.api.extensions.register_dataframe_accessor("Statistics")
class Statistics:
    def __init__(self, pandas_obj):
#        self._validate(pandas_obj)
        self.data = pandas_obj
        self.dfout = pd.DataFrame(index=self.data.index.copy())


    def common_statistics(self,mag=['mag'],drr='drr',
        args={'minimum occurrence (main direction) [%]':15,
        'folder out':os.getcwd(),
        'time blocking':{'yearly':True,
        'south hemisphere(Summer/Winter)':False,
        'south hemisphere 4 seasons':False,
        'north hemishere(Summer/Winter)':False,
        'north hemisphere 4 seasons':False,        
        'north hemisphere moosoon(SW,NE,Hot season)':False},
        'stats':"n min max mean std [1,5,10,50,90,95,99]",
                                                            }):
        """Extract statistics from a Panda dataframe column

            Parameters
            ~~~~~~~~~~

            mag : str
                Name of the column from which to get stats.
                Can be a list for extracting stats from multilple columns.
            drr : str, optional
                Column name representing the directions.
            args: dict
                Dictionnary with the folowing keys:

                    minimum occurrence (main direction) [%]: int
                        Use to calculate the main direction. Main direction is when
                        occurence>= Minimum occurrence. Default is 15
                    folder out: str
                        Path to save the output
                    time blocking: str
                         if ``time blocking=='yearly'``,
                            Statistics will be calculated for the whole timeserie
                         if ``time blocking=='south hemisphere(Summer/Winter)'``,
                            Statistics will be calculated for South hemisphere summer and winter seasons
                         if ``time blocking=='south hemisphere 4 seasons'``,
                            Statistics will be calculated for each South hemisphere seasons
                         if ``time blocking=='north hemishere(Summer/Winter)'``,
                            Statistics will be calculated for North hemisphere summer and winter seasons
                         if ``time blocking=='north hemisphere 4 seasons'``,
                            Statistics will be calculated for each North hemisphere seasons
                         if ``time blocking=='north hemisphere moosoon(SW,NE,Hot season)'``,
                            Statistics will be calculated for the North hemisphere moonsoon seasons
                    stats: str
                        string containing the name of the stats to do (must be numpy function)
                        exemple: ``n min max mean std [1,5,10,50,90,95,99]``,
                        where:
                         - n is for number of sample
                         - Put exceedence values in ``[]``


            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].Statistics.common_stats(mag='U',drr='drr',args={'time blocking':'Yearly'})
            >>> 
            
            Outputs:
            ~~~~~~~~
            .. list-table:: Common statistics example
               :widths: 25 25 25 25 25 25 25 25 25
               :header-rows: 1

               * - 
                 - N
                 - min
                 - max
                 - mean
                 - std
                 - P1
                 - P90
                 - Main Direction

               * - June
                 - 
                 - 
                 - 
                 - 
                 - 
                 - 
                 - 
                 -
               * - July
                 - 
                 - 
                 - 
                 - 
                 - 
                 - 
                 - 
                 -
               * - Winter
                 - 
                 - 
                 - 
                 - 
                 - 
                 - 
                 - 
                 -
               * - Total
                 - 
                 - 
                 - 
                 - 
                 - 
                 - 
                 - 
                 -

        """

        
        # for key in args:
        #     if isinstance(args[key],dict):
        #         import pdb;pdb.set_trace()


        if drr not in self.data:
            drr='none'
        else:
            drr=self.data[drr]

        min_occ=args.get('minimum occurrence (main direction) [%]',15)

        stats=args.get('stats',"n min max mean std [1,5,10,50,90,95,99]")
        stats=stats.split(' ')
        statf=[]
        for stat_name in stats:
            if '[' in stat_name:
                statf.append(eval(stat_name))
            else:
                statf.append(stat_name)
        if not isinstance(drr,str):
            statf.append(np.nan)     

        hem=args.get('time blocking','yearly')
        filename=os.path.join(args.get('folder out',os.getcwd()),os.path.splitext(self.data.filename)[0]+'stat.xlsx')
        time=self.data.index

        if isinstance(mag,str):
            mag=[mag]

        for ma in mag:
            data=self.data[ma]
            do_stats(time,statf,data,drr,hem,filename,ma,min_occ)
    
    def comparison_statistics(self,measured='measured',hindcast='hindcast',args={'folder out':os.getcwd()}):
        """Extract comparions statistics such as BIAS,MAE,RMSE,MRAE

        Parameters
        ~~~~~~~~~~

        measured : str
            Name of the column representing the measure data.
        hindcast : str
            Name of the column representing the hindcast data.
        args: dict
            Dictionnary with the folowing keys:
                folder out: str
                    Path to save the output


        Examples:
        ~~~~~~~~~
        >>> df=tf['test1']['dataframe'].Statistics.comparison_statistics(measured='U',hindcast='u',args={'folder out':'/tmp'})
        >>> 

        Outputs:
        ~~~~~~~~
        .. list-table:: Comparison statistics example
           :widths: 25 25 25
           :header-rows: 1

           * - MAE
             - Mean Absolute Error
             - 
           * - RMSE
             - Root Mean Square Error
             - 
           * - MRAE
             - Mean Relative Absolute Error
             - 
           * - BIAS
             - BIAS
             -              
           * - SI
             - Scatter Index
             -    
           * - IOA
             - Index of Agreement
             -  
        """

        if not hasattr(self.data,'filename'):
            self.data.filename=''

        filename=os.path.join(args.get('folder out',os.getcwd()),os.path.splitext(self.data.filename)[0]+'compstat.xlsx')
        hind=self.data[hindcast].values
        meas=self.data[measured].values

        
        do_comp_stats(filename,hind,meas,hindcast)
        # if isinstance(error_message,str):
        #     return error_message


    def Directional_statistics(self,mag='mag',drr='drr',\
        args={
        'function':{'Max':True, 'Mean':False, 'Median':False, 'Min':False, 'Percentile':False, 'Prod':False, 'Quantile':False, 'Std':False, 'Sum':False, 'Var':False},
        'Percentile or Quantile': 0.1,
        'folder out':os.getcwd(),
        'direction binning':{'centered':True,'not-centered':False},
        'direction interval': 45.,
        'time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
        }):

        """Extract statistics for the selected directionnal bins

            Parameters
            ~~~~~~~~~~

            mag : str
                Name of the column from which to get stats.
            drr : str
                Column name representing the directions.
            args: dict
                Dictionnary with the folowing keys:
                    function: str
                        Name of the function to use, can be `Max`, `Mean`, `Median`, `Min`, `Percentile`
                        `Prod`, `Quantile`, `Std`, `Sum`, `Var`
                    Percentile or Quantile: float
                        Percentile or Quantile value depending on the function
                    direction binning: str
                        Can be `centered` or `not-centered` depending if the directionnal are centered over 0
                    direction interval: int
                        Dirctionnal interval for the bins in degrees
                    folder out: str
                        Path to save the output
                    Time blocking: str
                         if ``Time blocking=='Yearly'``,
                            Statistics will be calculated for the whole timeserie
                         if ``Time blocking=='South hemisphere(Summer/Winter)'``,
                            Statistics will be calculated for South hemisphere summer and winter seasons
                         if ``Time blocking=='South hemisphere 4 seasons'``,
                            Statistics will be calculated for each South hemisphere seasons
                         if ``Time blocking=='North hemishere(Summer/Winter)'``,
                            Statistics will be calculated for North hemisphere summer and winter seasons
                         if ``Time blocking=='North hemisphere 4 seasons'``,
                            Statistics will be calculated for each North hemisphere seasons
                         if ``Time blocking=='North hemisphere moosoon(SW,NE,Hot season)'``,
                            Statistics will be calculated for the North hemisphere moonsoon seasons

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].Statistics.Directional_statistics(mag='U',drr='drr',args={'direction interval':45,Time blocking':'Yearly'})
            >>> 

            Outputs:
            ~~~~~~~~
            .. list-table:: Directionnal statistics example
               :widths: 25 25 25 25 25 25
               :header-rows: 1

               * - MEAN
                 - N
                 - S
                 - E
                 - W
                 - Total
               * - January
                 - 
                 - 
                 -
                 -
                 -
               * - February
                 - 
                 - 
                 -
                 -
                 -
               * - Annual
                 - 
                 - 
                 -
                 -
                 -
        """

        Ydata=self.data[mag]
        Xdata=self.data[drr]

        filename=os.path.join(args.get('folder out',os.getcwd()),os.path.splitext(self.data.filename)[0]+'directional_max.xlsx')

        X_interval=dir_interval(args['direction interval'],args['direction binning'])
        funct=getattr(np,'nan'+args['function'].lower())
        val=args['Percentile or Quantile']
        if hasattr(self.data[mag],'short_name'):
            short_name=self.data[mag].short_name
        else:
            short_name=mag
        do_directional_stat(filename,funct,val,short_name,self.data.index,Xdata,Ydata,X_interval,args['time blocking'],args['direction binning'])


    def joint_probability(self,mag='speed',drr='direction',period='period',\
        args={'method':{'Mag vs Dir':True,'Per Vs Dir':False,'Mag vs Per':False},\
        'folder out':os.getcwd(),
        'X Min Res Max(optional)':[2,1,22],
        'Y Min Res Max(optional)':[0,0.5],
        'direction binning':{'centered':True,'not-centered':False},
        'direction interval': 45.,
        'time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
        'probablity expressed in':{'percent':False,'per thoushand':True}
        }):
        """This function provides joint distribution tables for X and Y, i.e. the
            probability of events defined in terms of both X and Y (per 1000)
            It can be applied for magnitude-direction, magnitude-period or
            period-direction

            Parameters
            ~~~~~~~~~~

            mag : str
                Name of the column from which to get stats.
            drr : str
                Column name representing the directions. If method is `Per Vs Dir` or `Mag vs Dir`
            period : str
                Column name representing the period. If method is `Per Vs Dir` or `Mag vs Per`
            args: dict
                Dictionnary with the folowing keys:
                    method: str
                        Name of the method to use, can be:
                        `Mag vs Dir`: Plot Maginitude Versus Direction
                        `Per Vs Dir`: Plot Period Versus Direction
                        `Mag vs Per`: Plot Maginitude Versus Period
                    direction binning: str
                        Can be `centered` or `not-centered` depending if the directionnal are centered over 0
                    direction interval: int
                        Dirctionnal interval for the bins in degrees
                    folder out: str
                        Path to save the output
                    probablity expressed in: str
                        This can be `percent` or `per thoushand`
                    X Min Res Max(optional): list
                        Minimum, resolution and maximum value of X axis use in the join probability
                    Y Min Res Max(optional): list
                        Minimum, resolution and maximum value of Y axis use in the join probability
                    Time blocking: str
                         if ``Time blocking=='Annual'``,
                            Statistics will be calculated for the whole timeserie
                         if ``Time blocking=='Seasonal (South hemisphere)'``,
                            Statistics will be calculated for each South hemisphere seasons
                         if ``Time blocking=='Seasonal (North hemisphere)'``,
                            Statistics will be calculated for each North hemisphere seasons
                         if ``Time blocking=='Monthly'``,
                            Statistics will be calculated for each month

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].Statistics.joint_probability(mag='U',drr='drr',args={'direction interval':45,Time blocking':'Yearly'})
            >>> 

            Outputs:
            ~~~~~~~~
            .. list-table:: Joint probability example
               :widths: 25 25 25 25 25 25
               :header-rows: 1

               * - January
                 - 0
                 - 1
                 - 2
                 - 3
                 - Total
               * - 0
                 - 
                 - 
                 -
                 -
                 - 
               * - 1
                 - 
                 - 
                 -
                 -
                 -
               * - 2
                 - 
                 - 
                 -
                 -
                 -
               * - Total
                 - 
                 - 
                 -
                 -
                 - 100
        """
        analysis_method=args.get('method','Mag vs Dir')

        if analysis_method=='Mag vs Dir':
            Ydata=self.data[mag]
            Xdata=self.data[drr]

        elif analysis_method=='Per Vs Dir':
            Ydata=self.data[period]
            Xdata=self.data[drr]
        elif analysis_method=='Mag vs Per':
            Ydata=self.data[mag]
            Xdata=self.data[period]


        if not hasattr(self.data,'filename'):
            self.data.filename=''
        filename=os.path.join(args.get('folder out',os.getcwd()),os.path.splitext(self.data.filename)[0]+'JP.xlsx')

        if args.get('probablity expressed in','percent')=='percent':
            multiplier=100.
        else:
            multiplier=1000.
        Y_interval=get_increment(Ydata,args['Y Min Res Max(optional)'])
        

        if analysis_method=='Mag vs Dir' or analysis_method=='Per Vs Dir':
            X_interval=dir_interval(args.get('direction interval',45),
                args.get('direction binning','centered'))
            binning=args.get('direction binning','centered')
        else:
            X_interval=get_increment(Xdata,args['X Min Res Max(optional)'])
            binning=''
        

        X_interval=np.append(X_interval,np.nan)
        Y_interval=np.append(Y_interval,np.nan)
        do_joint_prob(filename,self.data.index,Xdata,Ydata,X_interval,Y_interval,
            args.get('time blocking','Annual'),binning,multiplier,mag)



    def weather_window(self,data='data',\
        args={'method':{'persistence exceedence':False,'persistence non-exceedence':True},\
        'folder out':os.getcwd(),
        'Exceedance bins: Min Res Max(optional)':[2,1,22],
        'Duration Min Res Max':[6,6,72],
        'time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
         }):
        """This function calculates the averaged number of full windows for data
            -exceeding specific values during a specific duration (persistence exceedence)
            -non-exceeding specific values during a specific duration (persistence non-exceedence)
            Note: if a window overlaps to the next month/season/year, it is assumed to belong to the
            month/season/year when the window starts.

            Parameters
            ~~~~~~~~~~

            data : str
                Name of the column from which to get stats.
            args: dict
                Dictionnary with the folowing keys:
                    method: str
                        It can be `persistence exceedence` or `persistence non-exceedence`
                    Exceedance bins: Min Res Max(optional): list
                        Minimum, resolution and maximum value of X axis to use
                    Duration Min Res Max: list
                        Minimum, resolution and maximum duration to use in hours
                    folder out: str
                        Path to save the output
                    Time blocking: str
                         if ``Time blocking=='Annual'``,
                            Statistics will be calculated for the whole timeserie
                         if ``Time blocking=='Seasonal (South hemisphere)'``,
                            Statistics will be calculated for each South hemisphere seasons
                         if ``Time blocking=='Seasonal (North hemisphere)'``,
                            Statistics will be calculated for each North hemisphere seasons
                         if ``Time blocking=='Monthly'``,
                            Statistics will be calculated for each month

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].Statistics.weather_window(data='U',args={'time blocking':'Monthly'})
            >>> 
            
            Outputs:
            ~~~~~~~~
            .. list-table:: Weather_window example
               :widths: 25 25 25 25 25 25
               :header-rows: 1

               * - 
                 - 6
                 - 12
                 - 18
                 - 24
                 - 36
               * - >0.2
                 - 
                 - 
                 - 
                 - 
                 - 
               * - >0.4
                 - 
                 - 
                 - 
                 - 
                 - 
               * - >0.6
                 - 
                 - 
                 - 
                 - 
                 - 
        """


        analysis=args.get('method','persistence non-exceedence') 
        filename=os.path.join(args.get('folder out',os.getcwd()),os.path.splitext(self.data.filename)[0]+'_WeatherWindow.xlsx')
        Ydata=self.data[data]
        Exc=get_increment(Ydata,args['Exceedance bins: Min Res Max(optional)'])
        duration=get_increment(Ydata,args['Duration Min Res Max'])
        do_window_stats(filename,self.data.index,Ydata,args['time blocking'],analysis,Exc,duration)

    def exceedence_probability(self,data='data',\
        args={'method':{'persistence exceedence':True,'persistence non-exceedence':False,\
        'exceedence':False,'non-exceedence':False},\
        'folder out':os.getcwd(),
        'exceedance bins: Min Res Max(optional)':[2,1,22],
        'duration Min Res Max':[6,6,72],
        'time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
         }):
        """This function calculates the frequency of occurrence of data:
            -exceeding specific values (exceedence)
            -non-exceeding specific values (non-exceedence)
            -exceeding specific values during a specific duration (persistence exceedence)
            -non-exceeding specific values during a specific duration (persistence non-exceedence)

            Parameters
            ~~~~~~~~~~

            data : str
                Name of the column from which to get stats.
            args: dict
                Dictionnary with the folowing keys:
                    method: str
                        It can be `exceedence`,`non-exceedence`, `persistence exceedence` or `persistence non-exceedence`
                    exceedance bins: Min Res Max(optional): list
                        Minimum, resolution and maximum value of X axis to use
                    duration Min Res Max: list
                        Minimum, resolution and maximum duration to use in hours
                    folder out: str
                        Path to save the output
                    time blocking: str
                         if ``Time blocking=='Annual'``,
                            Statistics will be calculated for the whole timeserie
                         if ``Time blocking=='Seasonal (South hemisphere)'``,
                            Statistics will be calculated for each South hemisphere seasons
                         if ``Time blocking=='Seasonal (North hemisphere)'``,
                            Statistics will be calculated for each North hemisphere seasons
                         if ``Time blocking=='Monthly'``,
                            Statistics will be calculated for each month

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].Statistics.weather_window(data='U',args={'time blocking':'Monthly'})
            >>> 
            
            Outputs:
            ~~~~~~~~
            .. list-table:: Weather_window example
               :widths: 25 25 25 25 25 25
               :header-rows: 1

               * - 
                 - 6
                 - 12
                 - 18
                 - 24
                 - 36
               * - >0.2
                 - 
                 - 
                 - 
                 - 
                 - 
               * - >0.4
                 - 
                 - 
                 - 
                 - 
                 - 
               * - >0.6
                 - 
                 - 
                 - 
                 - 
                 - 
        """




        analysis=args['method'] 
        filename=os.path.join(args.get('folder out',os.getcwd()),os.path.splitext(self.data.filename)[0]+'_'+analysis.replace(' ','_').replace('-','')+'_stat.xlsx')
        Ydata=self.data[data]
        Exc=get_increment(Ydata,args['exceedance bins: Min Res Max(optional)'])
        duration=get_increment(Ydata,args['duration Min Res Max'])
        do_exc_stats(filename,self.data.index,Ydata,args['time blocking'],analysis,Exc,duration,data)


    def excedence_coincidence_probability(self,data='data',coincident_nodir='coincident_nodir',coincident_with_dir='coincident_with_dir',\
        args={'method':{'exceedence':True,'non-exceedence':False},\
        'folder out':os.getcwd(),
        'Exceedance bins: Min Res Max(optional)':[0,2],
        'Coincidence bins: Min Res Max(optional)':[0,2],
        'Duration Min Res Max':[6,6,72],
        'direction binning':{'centered':True,'not-centered':False},
        'direction interval': 45.,
        'time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
         }):

        """Exceedence and non-exceedence analysis co-incident with another
            parameter, similar to Joint-probability function but includes a
            cumulative sum to obtain exceedence or non-exceedence(in %).

            Parameters
            ~~~~~~~~~~

            data : str
                Name of the column from which to get stats.
            coincident_with_dir : str
                Column name representing the directions. 
            coincident_nodir : str
                Column name representing another magnitude.
            args: dict
                Dictionnary with the folowing keys:
                    method: str
                        Name of the method to use, can be:
                        `exceedence`
                        `non-exceedence`
                    direction binning: str
                        Can be `centered` or `not-centered` depending if the directionnal are centered over 0
                    direction interval: int
                        Dirctionnal interval for the bins in degrees
                    folder out: str
                        Path to save the output
                    Probablity expressed in: str
                        This can be `percent` or `per thoushand`
                    Exceedance bins: Min Res Max(optional): list
                        Minimum, resolution and maximum value of X axis use in the join probability
                    Coincidence bins: Min Res Max(optional): list
                        Minimum, resolution and maximum value of Y axis use in the join probability
                    Time blocking: str
                         if ``Time blocking=='Annual'``,
                            Statistics will be calculated for the whole timeserie
                         if ``Time blocking=='Seasonal (South hemisphere)'``,
                            Statistics will be calculated for each South hemisphere seasons
                         if ``Time blocking=='Seasonal (North hemisphere)'``,
                            Statistics will be calculated for each North hemisphere seasons
                         if ``Time blocking=='Monthly'``,
                            Statistics will be calculated for each month

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].Statistics.excedence_coincidence_probability(data='U',coincident_with_dir='drr',args={'direction interval':45,Time blocking':'Yearly'})
            >>> 

            Outputs:
            ~~~~~~~~
            .. list-table:: Excedence coincidence probability
               :widths: 25 25 25 25 25 25
               :header-rows: 1

               * - exceedence %
                 - 0.0-0.2
                 - 0.2-0.4
                 - 0.4-0.6
                 - 0.6-0.8
                 - Total
               * - >0.0
                 - 
                 - 
                 -
                 -
                 - 
               * - >0.2
                 - 
                 - 
                 -
                 -
                 -
               * - >0.4
                 - 
                 - 
                 -
                 -
                 -
        """
        analysis=args['method'] 
        filename=os.path.join(args.get('folder out',os.getcwd()),os.path.splitext(self.data.filename)[0]+'_ExCoincstat.xlsx')
        Y=self.data[data]
        Exc=get_increment(Y,args['Exceedance bins: Min Res Max(optional)'])
        if coincident_nodir=='none':
            analysis_method='Mag_Dir'
            X=self.data[coincident_with_dir]
            X_interval=dir_interval(args['direction interval'],args['direction binning'])
            binning=args['direction binning']
        else:
            analysis_method='Mag_Var'
            X=self.data[coincident_nodir]
            X_interval=get_increment(Y,args['Coincidence bins: Min Res Max(optional)'])
            binning=''
            

        do_exc_coinc_stats(filename,self.data.index,X,Y,Exc,X_interval,args['time blocking'],analysis_method,analysis,binning)


    def workability(self,variables=['data1'],\
        args={'method':{'persistence exceedence':True,'persistence non-exceedence':False},\
               'folder out':os.getcwd(),
               'threshold for each dataset':[1,10], 
               'duration min res max':[6,6,72], 
               'time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
        }):

        """This function provides workability persistence (non-)exceedence tables, 
            i.e. the % of workable time based on limiting
            paramters (e.g. Hs < 2m and Wind speed < 10 m/s)

            Parameters
            ~~~~~~~~~~

            variables : list
                Name of the column use to create the conditions .
            args: dict
                Dictionnary with the folowing keys:
                    method: str
                        Name of the method to use, can be:
                        `persistence exceedence` default
                        `persistence non-exceedence`
                    threshold for each dataset: list
                        list of threshold to use for each of the paramater listed in `data`.
                        `data` and `Threshold` must have the same length
                    duration min res max: int
                        Duration interval in hours
                    folder out: str
                        Path to save the output
                    Time blocking: str
                         if ``Time blocking=='Annual'``,
                            Statistics will be calculated for the whole timeserie
                         if ``Time blocking=='Seasonal (South hemisphere)'``,
                            Statistics will be calculated for each South hemisphere seasons
                         if ``Time blocking=='Seasonal (North hemisphere)'``,
                            Statistics will be calculated for each North hemisphere seasons
                         if ``Time blocking=='Monthly'``,
                            Statistics will be calculated for each month

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].Statistics.workability(data=['hs','tp'],args={'Threshold':[2,15],Time blocking':'Yearly'})
            >>> 

            Outputs:
            ~~~~~~~~
            .. list-table:: Workability probability
               :widths: 25 25 25 25 25 25
               :header-rows: 1

               * - 
                 - >6
                 - >12
                 - >18
                 - >24
                 - >36
               * - January
                 - 
                 - 
                 -
                 -
                 - 
               * - February
                 - 
                 - 
                 -
                 -
                 -
        """

        analysis=args.get('method','persistence exceedence') 
        filename=os.path.join(args.get('folder out',os.getcwd()),os.path.splitext(self.data.filename)[0]+'_Workability.xlsx')
        duration=get_increment(self.data[variables],args['duration min res max'])
        Exc=args['threshold for each dataset']
        
        
        if len(variables)!=len(Exc):
            return 'The number of thresholds differs from the number of selected parameters'


        do_workability(filename,self.data[variables],Exc,duration,args['time blocking'],analysis)


    def wave_population(self,Hs='Hs',Tm02='Tm02',Drr_optional='Drr_optional',Tp_optional='Tp_optional',SW_optional='SW',\
            args={'Method':{'Height only':True,'Height/Direction':False,'Height/Tp':False,'Height/period':False},
                'direction binning':{'centered':True,'not-centered':False},
                'direction interval': 45.,
                'Heigh bin size': 0.5,
                'Period bin size': 2,
                'Exposure (years) (= length of time series if not specified)':0,
                'folder out':os.getcwd(),
                'directional switch':{'On':True,'Off':False}
            }):


        """ This function computes the wave population for fatigue analysis
            - Based on Rayleigh distribution if spectral width parameter (SW) is not
              specified.
            - Based on Longuet-Higgins Hs-Tp joint probability distribution if SW is
              specified

            Parameters
            ~~~~~~~~~~

            Hs : str
                Name of the column containing significant wave height.
            Tm02: str
                Name of the column containing the mean wave period using spectral moments of order 0 and 
            Drr_optional: str
                Optional column containing the direction
            Tp_optional: str
                Optional column containing the wave period
            SW_optional: str
                Optional column containing the spectral width parameter
            args: dict
                Dictionnary with the folowing keys:
                    Method: str
                        Name of the method to use, can be:
                        `Height only`
                        `Height/Direction`
                        `Height/Tp`
                        `Height/period`
                    direction binning: str
                        Can be `centered` or `not-centered` depending if the directionnal are centered over 0
                    direction interval: int
                        Dirctionnal interval for the bins in degrees
                    Heigh bin size: float
                        Interval in meter for Hs
                    Period bin size': float
                        Interval in second for the period
                    Exposure (years) (= length of time series if not specified): int
                        Number of years use, length of time series if not specified
                    folder out: str
                        Path to save the output
                    directional switch: str
                        Can be `On` or `Off` to use direction
            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].Statistics.wave_population(data=['hs','tp'],args={'Threshold':[2,15],Time blocking':'Yearly'})
            >>> 

            Outputs:
            ~~~~~~~~
            .. list-table:: Workability probability
               :widths: 25 25 25 25 25 25
               :header-rows: 1

               * - 
                 - Omni
                 - N
                 - S
                 - E
                 - W
               * - > 0.0 <= 0.1
                 - 
                 - 
                 -
                 -
                 - 
               * - > 0.1 <= 0.2
                 - 
                 - 
                 -
                 -
                 -
               * - > 0.2 <= 0.3
                 - 
                 - 
                 -
                 -
                 -
               * - Total
                 - 
                 - 
                 -
                 -
                 - 
        """
        if args['directional switch']=='On':
            drr_switch=True
        else:
            drr_switch=False
        filename=os.path.join(args.get('folder out',os.getcwd()),os.path.splitext(self.data.filename)[0]+'_Wavepop.xlsx')
        method=args['Method']
        Ddir=dir_interval(args['direction interval'],args['direction binning'])
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
                                                    'time blocking':{'South hemisphere(Summer/Winter)':True,\
                                                            'South hemisphere 4 seasons': False,
                                                            'North hemishere(Summer/Winter)':False,
                                                            'North hemisphere moosoon(SW,NE,Hot season)':False,
                                                            'North hemisphere 4 seasons': False
                                                            }}):

    
        """ This function computes the modal period for a set of hs/tp
            The modal period is taken as the mean period of the top 5% of wave height

            Parameters
            ~~~~~~~~~~

            Hs : str
                Name of the column containing significant wave height.
            Tp: str
                Name of the column containing the wave period.
            args: dict
                Dictionnary with the folowing keys:
                    folder out: str
                        Path to save the output
                    Time blocking: str
                         if ``Time blocking=='South hemisphere(Summer/Winter)'``,
                            Statistics will be calculated for South hemisphere summer and winter seasons
                         if ``Time blocking=='South hemisphere 4 seasons'``,
                            Statistics will be calculated for each South hemisphere seasons
                         if ``Time blocking=='North hemishere(Summer/Winter)'``,
                            Statistics will be calculated for North hemisphere summer and winter seasons
                         if ``Time blocking=='North hemisphere 4 seasons'``,
                            Statistics will be calculated for each North hemisphere seasons
                         if ``Time blocking=='North hemisphere moosoon(SW,NE,Hot season)'``,
                            Statistics will be calculated for the North hemisphere moonsoon seasons

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].Statistics.modal_wave_period(Hs='hs',Tp='tp')
            >>> 

            Outputs:
            ~~~~~~~~
            .. list-table:: Modal wave period probability
               :widths: 25 25
               :header-rows: 1

               * - 
                 - Modal wave period
               * - January
                 - 
               * - February
                 - 
        """


        hem=args.get('time blocking','South hemisphere(Summer/Winter)')
        filename=os.path.join(args.get('folder out',os.getcwd()),os.path.splitext(self.data.filename)[0]+'modal_wave_period.xlsx')
        hs=self.data[Hs]
        tp=self.data[Tp];
        time=self.data.index
        do_modal_stat(time,hs,tp,hem,filename)     

    def weighted_direction(self,Hs='Hs',drr='drr',args={'folder out':os.getcwd(),
                                                    'time blocking':{'South hemisphere(Summer/Winter)':True,\
                                                            'South hemisphere 4 seasons': False,
                                                            'North hemishere(Summer/Winter)':False,
                                                            'North hemisphere moosoon(SW,NE,Hot season)':False,
                                                            'North hemisphere 4 seasons': False
                                                            }}):

    
        """This function computes the energy weighted-dreiction based on 
            input timeseries of Hs and Dir
            
            Parameters
            ~~~~~~~~~~

            Hs : str
                Name of the column containing significant wave height.
            drr: str
                Name of the column containing the direction.
            args: dict
                Dictionnary with the folowing keys:
                    folder out: str
                        Path to save the output
                    Time blocking: str
                         if ``Time blocking=='South hemisphere(Summer/Winter)'``,
                            Statistics will be calculated for South hemisphere summer and winter seasons
                         if ``Time blocking=='South hemisphere 4 seasons'``,
                            Statistics will be calculated for each South hemisphere seasons
                         if ``Time blocking=='North hemishere(Summer/Winter)'``,
                            Statistics will be calculated for North hemisphere summer and winter seasons
                         if ``Time blocking=='North hemisphere 4 seasons'``,
                            Statistics will be calculated for each North hemisphere seasons
                         if ``Time blocking=='North hemisphere moosoon(SW,NE,Hot season)'``,
                            Statistics will be calculated for the North hemisphere moonsoon seasons

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].Statistics.modal_wave_period(Hs='hs',Tp='tp')
            >>> 

            Outputs:
            ~~~~~~~~
            .. list-table:: Workability probability
               :widths: 25 25
               :header-rows: 1

               * - 
                 - Energy weighted direction
               * - January
                 - 
               * - February
                 - 
        """

        hem=args['time blocking']
        filename=os.path.join(args.get('folder out',os.getcwd()),os.path.splitext(self.data.filename)[0]+'weighted_direction.xlsx')
        hs=self.data[Hs]
        drr=self.data[drr];
        time=self.data.index
        do_weighted_direction(time,hs,drr,hem,filename)   