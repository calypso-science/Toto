import pandas as pd
import os

from ...core.toolbox import get_opt,dir_interval
import numpy as np
#from ._do_EVA_general import do_EVA_general

@pd.api.extensions.register_dataframe_accessor("Extreme")
class Extreme:
    def __init__(self, pandas_obj):
        self.data = pandas_obj
        self.dfout = pd.DataFrame(index=self.data.index.copy())

    def do_extreme(self,magnitude='magnitude',tp_optional='tp_optional',direction_optional='direction_optional',tm_optional='tm_optional',\
        args={'threshold type':{'percentile':True,'value':False},
         'threshold value':0.0,
         'Directional':{'On':True,'Off':False},
         'Minimum time interval between peaks (h)':24.0,
         'Direction binning':{'centered':True,'not-centered':False},
         'Direction interval': 45.,
         'Time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
         'display':{'On':True,'Off':False},
         'Estimate Hmax & Cmax RPVs':{'On':False,'Off':True},
         'Water depth':5000.0,
         'folder out':'/tmp/'
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

        folderout=args['folder out']
        drr_interval=dir_interval(args['Direction interval'],args['Direction binning'])
        threshold_type=args['threshold type']
        directional_pot=False
        if args[Directional]=='On':
            directional_pot=True

        min_time=args['Minimum time interval between peaks (h)']
        time_blocking=args['Time blocking']
        display=True
        if args['display']=='Off':
            display=False
        Hmax_RPV=False
        if args['Estimate Hmax & Cmax RPVs']=='On':
            Hmax_RPV=False  

        water_depth=args['Water depth']      


        if direction_optional in self.data:
            drr=self.data[direction_optional].values
        else:
            drr=None

        if tp_optional in self.data:
            tp=self.data[tp_optional].values
        else:
            tp=None

        if tm_optional in self.data:
            tm=self.data[tm_optional].values
        else:
            tm=None

        # _do_EVA_general(self.data.index,self.data[magnitude],tp,drr,tm,
        #     dir_interval,threshold_type,directional_pot,min_time,time_blocking,display,Hmax_RPV,water_depth,folderout)



