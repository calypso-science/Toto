import pandas as pd
import os
from ...core.toolbox import display_message

@pd.api.extensions.register_dataframe_accessor("Extreme")

class Extreme:
    def __init__(self, pandas_obj):
        self.data = pandas_obj
        self.dfout = self.data.copy()

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


        """This function is used for extreme value analysis of total still water 
            elevation (surge + tide).
            Inputs must be surge and tide level (in the same unit).
            The method complies with ISO recommendations:
            return period values are estimated by fitting a distribution
            to the empirical distribution obtained by combining the
            joint frequency distribution of tidal and surge elevations.
        """

        display_message()

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
    

        """This function is used for extreme value analysis of any type.
        It generates return period values for any parameters.
        Inputs can be:
         -only magnitude (omni-directional extreme value ananlysis)
         -magnitute and direction (directional ARI with omni or directional POT)_
         -wave magnitude and period (omni-directional analysis and bi-variate,
          Hs vs. Tp, extremes, estimated using the FORM method)
         -wave magnitude, period and direction (directional ARI with omni or
          directional POT and bi-variate extremes, Hs vs. Tp, estimated using the
          FORM method for each selected directions)"""

        display_message()

    def do_extreme_adjusted(self,hs='magnitude',wspd_optional='tp_optional',\
        args={'Fitting distributionfor Hs':{'Weibull':True,'Gumbel':False,'GPD':False,'GEV':False},
         'Fitting distributionfor Wspd':{'Weibull':True,'Gumbel':False,'GPD':False,'GEV':False},
         'Estimation method for Hs':{'pkd':False,'pwm':False,'mom':False,'ml':True},
         'Estimation method for Wspd':{'pkd':False,'pwm':False,'mom':False,'ml':True},
         'Risk level: e.g. 10%, 5%, 1%':[10],
         'Max limiting Hs (typically 5 m for barge tow and 8 m for ships': 5,
         'Transport speed (m/s)':2.572,
         'Transport distance (km)':1000.0,
         'Time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
         'Display CDFs':{'On':True,'Off':False},
         'folder out':os.getcwd()
         }):
    

        """This function is used for adjusted extreme value analysis (Hs and wind speed)
           accuonting for time of exposure (typically for transportation metocean extremes). It generates
           return period values for Hs and Wspd. Inputs are: %Hs and Wsp (optional).
           Reference: GL Noble Denton, 2010. TECHNICAL POLICY BOARD, GUIDELINES FOR
           MARINE TRANSPORTATIONS. GL Noble Denton Group Ltd."""


        display_message()

