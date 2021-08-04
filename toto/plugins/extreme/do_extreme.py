import pandas as pd
import os
from ...core.toolbox import display_message,dir_interval
from ._extreme_tools import ExtremeBase
import numpy as np

@pd.api.extensions.register_dataframe_accessor("Extreme")
class Extreme(ExtremeBase):
    def __init__(self, pandas_obj):
         super(Extreme, self).__init__(pandas_obj)


    def distribution_shape(self,magnitude='magnitude',direction_optional='direction_optional',\
        args={'Fitting distribution':{'Weibull':True,'Gumbel':False,'GPD':False,'GEV':False},
         'Method':{'pkd':False,'pwm':False,'mom':False,'ml':True},
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
         'folder out':os.getcwd()
         }):

        """This function is used for distribution analysis of any type.
        It generates return the shape and scale of a distribution.
        Inputs can be:
         -only magnitude (omni-directional extreme value ananlysis)
         -magnitute and direction (directional ARI with omni or directional POT)_
        """

        # variabl check
        if direction_optional not in self.data:
            direction_optional=None

        folderout=os.path.join(args['folder out'])

        ## Inputs
        fitting=args['Fitting distribution']
        method=args['Method']
        min_peak=args['Minimum number of peaks over threshold']      

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
            print('No Peak found !!')
            return 'No Peak found !!'
        else:
            self._clean_peak()

        self._get_shape(magnitude,fitting,method,time_blocking,)

        if args['Display peaks']=='On':
            self._plot_peaks(magnitude,display=True,folder=folderout)
        else:
            self._plot_peaks(magnitude,display=False,folder=folderout)

        all_dirs=list(self.peaks_index['Annual'].keys())
        if args['Display CDFs']=='On':
            display=True
        else:
            display=False

        for all_dir in all_dirs:
            self._plot_cdfs(magnitude,drr=all_dir,display=display,folder=folderout)

        self._export_shape_as_xls([magnitude],fitting,filename=os.path.join(folderout,self.file+'Shape.xlsx'))


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

