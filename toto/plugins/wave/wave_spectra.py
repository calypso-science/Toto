import pandas as pd
import numpy as np
from ._do_ssh_to_wave import do_ssh_to_wave
from ._do_wave_spectra_plot import do_wave_spectra_plot
from ...core.toolbox import get_opt
from ...filters.bandpass_filter import bandpass_filter
import os

@pd.api.extensions.register_dataframe_accessor("WaveAnalysis")
class WaveAnalysis:
    def __init__(self, pandas_obj):
#        self._validate(pandas_obj)
        self.data = pandas_obj
        self.dfout = pd.DataFrame(index=self.data.index.copy())

    def wave_spectra_plot(self,sea_level='sea_level',\
        args={'units':'m',
         'Windows': 3600,
         'Overlap':1800,
         'Nfft':3600,
         'Detrend':{'Off':True,'linear':False,'constante':False},
         'Period (s) min and max for plotting':[10, 1000],
         'Xaxis':{'period':True,'frequency':False},
         'folder out':'/tmp/',
         'display':{'On':True,'Off':False}
         }):

        '''%This function estimated the 1D wave spectrum (Power Spectral Density) and plot it'''
        unit=get_opt(self.data[sea_level],'units',args['units'])
        display=True
        if args['display']=='Off':
            display=False

        detrend=False
        if args['Detrend']=='linear':
            detrend='linear'
        elif args['Detrend']== 'constant':
            detrend='constant'

        Xaxis=True
        if args['Xaxis']=='period':
            Xaxis=False
        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'_Spec.png')
        error=do_wave_spectra_plot(self.data.index,self.data[sea_level].values,unit,
            args['Windows'],
            args['Overlap'],
            args['Nfft'],
            detrend,args['Period (s) min and max for plotting'],Xaxis,filename,display)


    def ssh_to_wave_with_spectra(self,sea_level='sea_level',\
        args={
         'Windows': 3600,
         'Overlap':1800,
         'Nfft':3600,
         'Detrend':{'Off':True,'linear':False,'constante':False},
         'Wave period range (min and max) (in s)':[3, 25],
         }):
    

        detrend=False
        if args['Detrend']=='linear':
            detrend='linear'
        elif args['Detrend']== 'constant':
            detrend='constant'

        self.dfout=do_ssh_to_wave(self.data.index,self.data[sea_level].values,
            args['Overlap'],
            args['Nfft'],args['Windows'],detrend,args['Wave period range (min and max) (in s)'],0,method='spectra')

        self.dfout.index.name='time'
        return self.dfout


    def ssh_to_wave_with_0crossing(self,sea_level='sea_level',\
        args={
         'Windows': 3600,
         'Overlap':1800,
         'Nfft':3600,
         'Crossing':{'Downcrossing':True,'Upcrossing':False},
         'Wave period range (min and max) (in s)':[3, 25],
         'Minimum number of waves per window for zero crossing analysis': 30
         }):
    
        '''%This function extracts wave height statistics (Hs, H10, Hmax) and
        %corresponding periods (Ts, T10, Tmax) from a sea level time series using
        %zero corrsing analysis. The signal is band pass filtered within a
        %selected period range before applaying zero corrosing analysis'''

        period=args['Wave period range (min and max) (in s)']

        
        self.dfout=do_ssh_to_wave(self.data.index,self.data[sea_level].values,
            args['Overlap'],
            args['Nfft'],args['Windows'],args['Crossing'],
            period,
            args['Minimum number of waves per window for zero crossing analysis'],method='crossing')

        self.dfout.index.name='time'
        return self.dfout