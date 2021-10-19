import pandas as pd
import os
from ...core.toolbox import display_message,dir_interval
from ._extreme_tools import ExtremeBase
import numpy as np

@pd.api.extensions.register_dataframe_accessor("Extreme")
class Extreme(ExtremeBase):
    def __init__(self, pandas_obj):
         super(Extreme, self).__init__(pandas_obj)


    def distribution_shape(self,mag='magnitude',drr='direction',\
        args={'fitting distribution':{'Weibull':True,'Gumbel':False,'GPD':False,'GEV':False},
         'method':{'pkd':False,'pwm':False,'mom':False,'ml':True},
         'threshold type':{'percentile':True,'value':False},
         'threshold value':95.0,
         'directional':{'On':True,'Off':False},
         'minimum number of peaks over threshold': 30,
         'minimum time interval between peaks (h)':24.0,
         'direction binning':{'centered':True,'not-centered':False},
         'direction interval': 45.,
         'time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
         'display peaks':{'On':True,'Off':False},
         'display CDFs':{'On':True,'Off':False},
         'folder out':os.getcwd()
         }):

        """This function is used for distribution analysis of any type.
           It generates return the shape and scale of a distribution.
           Inputs can be:
                -only magnitude (omni-directional extreme value ananlysis)
                -magnitute and direction (directional ARI with omni or directional POT)_
            
            Parameters
            ~~~~~~~~~~

            mag : str
                Name of the column from which to get stats.
            drr : str optionnal
                Column name representing the directions.
            args: dict
                Dictionnary with the folowing keys:
                    fitting distribution: str
                        Name of the fit to use, can be: `Weibull`, `Gumbel`, `GPD` or `GEV`.
                    method: str
                        Name of the estimation method, can be:
                        `pkd`: Pickands’ estimator.
                        `pwm`: PWM-method
                        `mom`: Moment method
                        `ml` : Maximum Likelihood method
                    threshold type: str
                        Method to find the peaks:
                        `percentile`: using the th percentile
                        `value`: using a treshold value
                    threshold value: float
                        Either a absolute value or percentile value depending on the `threshold type`
                    directional: str
                        Can be `On` or `Off`, to calculate stats for each direction.
                        Needs `drr` variable
                    direction binning: str
                        Can be `centered` or `not-centered` depending if the directionnal are centered over 0
                    direction interval: int
                        Dirctionnal interval for the bins in degrees
                    minimum number of peaks over threshold: int
                    minimum time interval between peaks (h): int
                    display peaks: str
                        `On` or `Off` to display peaks over threshold
                    display CDFs: str
                        `On` or `Off` to display CFDs image
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
                            Statistics will be calculated for each 12 months

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].Extreme.distribution_shape(mag='U',drr='drr',args={'directional':'On',Time blocking':'Annual'})
            >>> 

            Outputs:
            ~~~~~~~~
            .. list-table:: Distribution shape
               :widths: 25 25 25
               :header-rows: 1

               * - Filename
                 - Scale
                 - Shape
               * - 
                 - 
                 - 
        """


        # variabl check
        if direction_optional not in self.data:
            direction_optional=None

        folderout=os.path.join(args.get('folder out',os.getcwd()))

        ## Inputs
        fitting=args.get('fitting distribution','Weibull')
        method=args.get('method','ml')
        min_peak=args['minimum number of peaks over threshold']      

        if args.get('directional','Off')=='On':
            drr_interval=dir_interval(args.get('direction interval',45),
                args.get('direction binning','centered'))
        else:
            drr_interval=[0,360]

        time_blocking=args.get('time blocking','Annual')
        pks_opt={}
        thresh=args.get('threshold value',95)
        if args.get('threshold type','percentile')=='percentile':
            sort_data=np.sort(self.dfout[mag].values)
            pks_opt['height']=sort_data[int(np.round(len(sort_data)*(thresh/100)))]
        else:
            pks_opt['height']=thresh

        pks_opt['distance']=args.get('minimum time interval between peaks (h)',24)*(self.sint/3600)

        self._get_peaks(mag,drr=drr,directional_interval=drr_interval,
            time_blocking=time_blocking,peaks_options=pks_opt,min_peak=min_peak)

        if 'Omni' not in self.peaks_index['Annual']:
            print('No Peak found !!')
            return 'No Peak found !!'
        else:
            self._clean_peak()

        self._get_shape(mag,fitting,method,time_blocking,)

        if args.get('display peaks','Off')=='On':
            self._plot_peaks(mag,display=True,folder=folderout)
        else:
            self._plot_peaks(mag,display=False,folder=folderout)

        all_dirs=list(self.peaks_index['Annual'].keys())
        if args.get('display CDFs','Off')=='On':
            display=True
        else:
            display=False


        for all_dir in all_dirs:
            self._plot_cdfs(mag,drr=all_dir,display=display,folder=folderout)

        self._export_shape_as_xls([mag],fitting,
            filename=os.path.join(folderout,self.file+'Shape.xlsx'))


    def extreme_water_elevation(self,tide='tide',surge='surge',
        args={'fitting distribution':{'Weibull':True,'Gumbel':False,'GPD':False,'GEV':False},
         'method':{'pkd':False,'pwm':False,'mom':False,'ml':True},
         'surge':{'Positive only':False,'Negative only':False,'Both (neg and pos)':True},
         'return period':[1,10,25,50,100],
         'threshold type':{'percentile':True,'value':False},
         'threshold value':95.0,
         'minimum number of peaks over threshold': 30,
         'minimum time interval between peaks (h)':24.0,
         'time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
         'display peaks':{'On':True,'Off':False},
         'display CDFs':{'On':True,'Off':False},
         'folder out':os.getcwd()
         }):


        """ This function is used for extreme value analysis of total still water 
            elevation (surge + tide).
            Inputs must be surge and tide level (in the same unit).
            The method complies with ISO recommendations:
            return period values are estimated by fitting a distribution
            to the empirical distribution obtained by combining the
            joint frequency distribution of tidal and surge elevations.

            Parameters
            ~~~~~~~~~~

            tide: str
                Column name representing the tide.
            surge: str optionnal
                Column name representing the surge.
            args: dict
                Dictionnary with the folowing keys:
                    fitting distribution: str
                        Name of the fit to use, can be: `Weibull`, `Gumbel`, `GPD` or `GEV`.
                    method: str
                        Name of the estimation method, can be:
                        `pkd`: Pickands’ estimator.
                        `pwm`: PWM-method
                        `mom`: Moment method
                        `ml` : Maximum Likelihood method
                    surge: str
                        Can be:
                        `Positive only`: use only positive surge
                        `Negative only`:use only negative surge
                        `Both (neg and pos)`: use both
                    return period: list
                        Return period values.
                    threshold type: str
                        Method to find the peaks:
                        `percentile`: using the th percentile
                        `value`: using a treshold value
                    threshold value: float
                        Either a absolute value or percentile value depending on the `threshold type`
                    minimum number of peaks over threshold: int
                    minimum time interval between peaks (h): int
                    display peaks: str
                        `On` or `Off` to display peaks over threshold
                    display CDFs: str
                        `On` or `Off` to display CFDs image
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
                            Statistics will be calculated for each 12 months

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].Extreme.extreme_water_elevation(tide='Et',surge='Eo',args={'Time blocking':'Annual'})
            >>> 

            Outputs:
            ~~~~~~~~
            .. list-table:: Extreme water elevation
               :widths: 25 25
               :header-rows: 1

               * - positive surge
                 - Omni
               * - 1
                 - 
               * - 10
                 - 
               * - 25
                 - 
               * -
                 -
               * - negative surge
                 - Omni
               * - 1
                 - 
               * - 10
                 - 
               * - 25
                 - 
        """

        display_message()

    def do_extreme(self,mag='magnitude',
        tp='tp_optional',
        drr='direction_optional',
        tm='tm_optional',
        water_depth='water_depth_optional',\
        args={'fitting distribution':{'Weibull':True,'Gumbel':False,'GPD':False,'GEV':False},
         'method':{'pkd':False,'pwm':False,'mom':False,'ml':True},
         'slope fitting distribution':{'Weibull':True,'Gumbel':False},
         'slope treshold':0.005,
         'return period':[1,10,25,50,100],
         'estimate Hmax & Cmax RPVs':{'On':False,'Off':True},
         'threshold type':{'percentile':True,'value':False},
         'threshold value':95.0,
         'directional':{'On':True,'Off':False},
         'minimum number of peaks over threshold': 30,
         'minimum time interval between peaks (h)':24.0,
         'direction binning':{'centered':True,'not-centered':False},
         'direction interval': 45.,
         'time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
         'display peaks':{'On':True,'Off':False},
         'display CDFs':{'On':True,'Off':False},
         'water depth':5000.0,
         'folder out':os.getcwd()
         }):
    

        """ This function is used for extreme value analysis of any type.
            It generates return period values for any parameters.
            Inputs can be:
             -only magnitude (omni-directional extreme value ananlysis)
             -magnitute and direction (directional ARI with omni or directional POT)_
             -wave magnitude and period (omni-directional analysis and bi-variate,
              Hs vs. Tp, extremes, estimated using the FORM method)
             -wave magnitude, period and direction (directional ARI with omni or
              directional POT and bi-variate extremes, Hs vs. Tp, estimated using the
              FORM method for each selected directions)
            
            Parameters
            ~~~~~~~~~~

            mag : str
                Name of the column from which to get stats.
            tp : str optionnal
                Column name representing the peak period.
            tm : str optionnal
                Column name representing Tm02.
            drr : str optionnal
                Column name representing the directions.
            water_depth : str optionnal
                Column name representing the water elevation.
            args: dict
                Dictionnary with the folowing keys:
                    fitting distribution: str
                        Name of the fit to use, can be: `Weibull`, `Gumbel`, `GPD` or `GEV`.
                    method: str
                        Name of the estimation method, can be:
                        `pkd`: Pickands’ estimator.
                        `pwm`: PWM-method
                        `mom`: Moment method
                        `ml` : Maximum Likelihood method
                    threshold type: str
                        Method to find the peaks:
                        `percentile`: using the th percentile
                        `value`: using a treshold value
                    threshold value: float
                        Either a absolute value or percentile value depending on the `threshold type`
                    slope fitting distribution: str
                        Can be: `Weibull`, `Gumbel`
                    slope threshold: float
                    return period: list
                        Return period values.      
                    estimate Hmax & Cmax RPVs: str
                        Can be `On` or `Off`
                    water depth: float
                        Total water depth if not specified in the input
                    directional: str
                        Can be `On` or `Off`, to calculate stats for each direction.
                        Needs `drr` variable
                    direction binning: str
                        Can be `centered` or `not-centered` depending if the directionnal are centered over 0
                    direction interval: int
                        Dirctionnal interval for the bins in degrees
                    minimum number of peaks over threshold: int
                    minimum time interval between peaks (h): int
                    display peaks: str
                        `On` or `Off` to display peaks over threshold
                    display CDFs: str
                        `On` or `Off` to display CFDs image
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
                            Statistics will be calculated for each 12 months

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].Extreme.do_extreme(mag='U',args={'directional':'On',Time blocking':'Annual'})
            >>> 

            Outputs:
            ~~~~~~~~
            .. list-table:: Extreme value
               :widths: 25 25 25 25 25 25
               :header-rows: 1

               * - 
                 - Omni
                 - N
                 - E
                 - W
                 - S
               * - 1
                 - 
                 -
                 -
                 -
                 -
               * - 10
                 - 
                 -
                 -
                 -
                 -
               * - 100
                 - 
                 -
                 -
                 -
                 -

        """

        display_message()

    def do_extreme_adjusted(self,hs='magnitude',wspd='wind_optional',\
        args={'fitting distribution for Hs':{'Weibull':True,'Gumbel':False,'GPD':False,'GEV':False},
         'fitting distribution for Wspd':{'Weibull':True,'Gumbel':False,'GPD':False,'GEV':False},
         'estimation method for Hs':{'pkd':False,'pwm':False,'mom':False,'ml':True},
         'estimation method for Wspd':{'pkd':False,'pwm':False,'mom':False,'ml':True},
         'risk level':[10],
         'max limiting Hs': 5,
         'transport speed (m/s)':2.572,
         'transport distance (km)':1000.0,
         'time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
         'display CDFs':{'On':True,'Off':False},
         'folder out':os.getcwd()
         }):
    

        """ This function is used for adjusted extreme value analysis (Hs and wind speed)
            accuonting for time of exposure (typically for transportation metocean extremes). It generates
            return period values for Hs and Wspd. Inputs are: %Hs and Wsp (optional).
            Reference: GL Noble Denton, 2010. TECHNICAL POLICY BOARD, GUIDELINES FOR
            MARINE TRANSPORTATIONS. GL Noble Denton Group Ltd.

            Parameters
            ~~~~~~~~~~

            hs : str
                Column name representing the wave height
            wspd : str optionnal
                Column name representing the wind speed.
            args: dict
                Dictionnary with the folowing keys:
                    fitting distribution for Hs: str
                        Name of the fit to use, can be: `Weibull`, `Gumbel`, `GPD` or `GEV`.
                    fitting distribution for Wspd: str
                        Name of the fit to use, can be: `Weibull`, `Gumbel`, `GPD` or `GEV`.
                    estimation method for Hs: str
                        Name of the estimation method, can be:
                        `pkd`: Pickands’ estimator.
                        `pwm`: PWM-method
                        `mom`: Moment method
                        `ml` : Maximum Likelihood method
                    estimation method for Wspd: str
                        Name of the estimation method, can be:
                        `pkd`: Pickands’ estimator.
                        `pwm`: PWM-method
                        `mom`: Moment method
                        `ml` : Maximum Likelihood method
                    risk level: list
                        percentage for the risk level
                    max limiting Hs: float
                        Typically 5 m for barge tow and 8 m for ships
                    transport speed (m/s): float
                        Boat in speed in m/s
                    transport distance (km): float
                    display CDFs: str
                        `On` or `Off` to display CFDs image
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
                            Statistics will be calculated for each 12 months

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].Extreme.do_extreme_adjusted(hs='hs',args={'transport speed (m/s)':2.5,'transport distance (km)': 100,'time blocking':'Annual'})
            >>> 

            Outputs:
            ~~~~~~~~
            .. list-table:: Extreme value
               :widths: 25 25 25 25 25 25
               :header-rows: 1

               * - 
                 - Omni
                 - N
                 - E
                 - W
                 - S
               * - 1
                 - 
                 -
                 -
                 -
                 -
               * - 10
                 - 
                 -
                 -
                 -
                 -
               * - 100
                 - 
                 -
                 -
                 -
                 -

        """
        display_message()

