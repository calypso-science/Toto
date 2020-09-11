import pandas as pd
from ...core.toolbox import dir_interval,get_increment
import os
from toto.plugins.statistics._do_stats import do_stats
from ._wood_joint_prob import do_joint_prob
from ._wood_pers_prob import do_perc_stats
from ._wood_extreme_stat import do_extrem_stats
import numpy as np

@pd.api.extensions.register_dataframe_accessor("Woodside")
class Woodside:
    def __init__(self, pandas_obj):
#        self._validate(pandas_obj)
        self.data = pandas_obj
        self.dfout = pd.DataFrame(index=self.data.index.copy())


    def woodside_statistics(self,mag='mag',drr='drr',args={'folder out':os.getcwd(),
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
        do_joint_prob(filename,self.data.index,Xdata,Ydata,X_interval,Y_interval,args['Time blocking'],binning,multiplier)



    def persistence_probability(self,data='data',\
        args={'method':{'exceedence':True,'non-exceedence':False},\
        'folder out':os.getcwd(),
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
        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'_Pers.xlsx')
        Ydata=self.data[data]
        Exc=get_increment(Ydata,args['Exceedance bins: Min Res Max(optional)'])
        duration=get_increment(Ydata,args['Duration Min Res Max'])
        do_perc_stats(filename,self.data.index,Ydata,args['Time blocking'],analysis,Exc,duration)


    def extreme_analysis(self,wind_speed10='wind_speed10',wind_drr='wind_drr',
                          hs='hs',tp='tp',tm02='tm02',dpm='dpm',
                          surface_current='surface_current',surface_drr='surface_drr',
                          midwater_current='midwater_current',midwater_drr='midwater_drr',
                          bottom_current='bottom_current',bottom_drr='bottom_drr',
                          args={'return_period': [1,5,10,20,50,100,200,500,1000],
                          'Display':{'On':True,'Off':False},
                          'Water depth':5000.,
                          'Directional switch':{'On':True,'Off':False},
                          'folder out':os.getcwd(),
                           }):

        if args['Directional switch']=='On':
            drr_interval=dir_interval()
        else:
            drr_interval=[0,360]

        rv=args['return_period']
        if ~isinstance(rv,np.ndarray):
            rv=np.array(rv)

        display=False
        if args['Display']=='On':
            display=True
        h=args['Water depth']
        folderout=args['folder out']


        do_extrem_stats(self.data[wind_speed10],self.data[wind_drr],
            self.data[hs],self.data[tp],self.data[tm02],self.data[dpm],
            self.data[surface_current],self.data[surface_drr],
            self.data[midwater_current],self.data[midwater_drr],
            self.data[bottom_current],self.data[bottom_drr],
            drr_interval,rv,display,h,folderout)