import pandas as pd
import numpy as np
from ._do_ssh_to_wave import do_ssh_to_wave
from ._do_wave_spectra_plot import do_wave_spectra_plot
from ._do_wavelet_analysis import do_wavelet
from ...core.toolbox import get_opt
from ...filters.bandpass_filter import bandpass_filter
import os

@pd.api.extensions.register_dataframe_accessor("WaveAnalysis")
class WaveAnalysis:
    def __init__(self, pandas_obj):
#        self._validate(pandas_obj)
        self.data = pandas_obj
        self.dfout = pd.DataFrame(index=self.data.index.copy())

    def wave_spectra(self,sea_level='sea_level',\
        args={'units':'m',
         'Windows': 3600,
         'Overlap':1800,
         'Nfft':3600,
         'Detrend':{'Off':True,'linear':False,'constante':False},
         'Period (s) min and max for plotting':[10, 1000],
         'Xaxis':{'period':True,'frequency':False},
         'folder out':os.getcwd(),
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


    def ssh_to_wave(self,sea_level='sea_level',\
        args={
         'Windows': 3600,
         'Overlap':1800,
         'Nfft':3600,
         'Detrend':{'Off':True,'linear':False,'constante':False},
         'Wave period range (min and max) (in s)':[3, 25],
         'Method':{'spectra':True,'zero-crossing':False},
         'Minimum number of waves per window for zero crossing analysis': 30,
         'Crossing':{'Downcrossing':True,'Upcrossing':False},
         }):
        


        min_wave=args['Minimum number of waves per window for zero crossing analysis']
        period=args['Wave period range (min and max) (in s)']
        method=args['Method']
        if method=='zero-crossing':
            self.data[sea_level]=bandpass_filter(self.data[sea_level],args={'lower cut-off (s)':period[0],'upper cut-off (s)':period[1]})




        detrend=False
        if args['Detrend']=='linear':
            detrend='linear'
        elif args['Detrend']== 'constant':
            detrend='constant'

        crossing=False
        if args['Crossing']=='Upcrossing':
            crossing=True

        self.dfout=do_ssh_to_wave(self.data.index,self.data[sea_level].values,
            args['Overlap'],
            args['Nfft'],args['Windows'],detrend,period,min_wave,crossing,method)

        self.dfout.index.name='time'

        return self.dfout


    def wavelet_analysis(self,sea_level='sea_level',\
        args={
         'units':'m',
         'Mother wavelet':{'Morlet':True,'Paul':False,'DOG':False},
         'Wave period range (min and max) (in s)':[3, 25],
         'Number of sub-ocatve per period band': 8,
         'folder out':os.getcwd(),
         'display':{'On':True,'Off':False}
         }):
        

        '''%This function estimates the wavelet power spectrum of a time series, as
        %well as the scaled-averaged wavelet power time series within a specific
        %period band. The code is based on the wavelet toolbox from Torrence and
        %Compo (http://paos.colorado.edu/research/wavelets/)'''

        display=True
        if args['display']=='Off':
            display=False
        filename=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'_Wavelet.png')
        period=args['Wave period range (min and max) (in s)']


        unit=get_opt(self.data[sea_level],'units',args['units'])

        do_wavelet(self.data.index,self.data[sea_level],
            args['Mother wavelet'],period,args['Number of sub-ocatve per period band'],
            unit,filename,display)