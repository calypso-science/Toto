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
         'windows': 3600,
         'overlap':1800,
         'nfft':3600,
         'detrend':{'Off':True,'linear':False,'constante':False},
         'period (s) min and max for plotting':[10, 1000],
         'xaxis':{'period':True,'frequency':False},
         'folder out':os.getcwd(),
         'display':{'On':True,'Off':False}
         }):

        """ This function estimated the 1D wave spectrum (Power Spectral Density)
            and plot it

            Parameters
            ~~~~~~~~~~

            sea_level : str
                Name of the column which contains the sea level.
            args: dict
                Dictionnary with the folowing keys:
                units: str
                    Units of the sea level
                windows: int
                    windows to process in seconds.
                overlap: int
                    overlap in seconds
                nfft: int
                     Length of the signal to calculate the Fourier transform of.
                detrend: str
                    `linear`, `constante` or `Off` to detrend the timeseries before doing the analysis
                period (s) min and max for plotting: list
                    X axis limit in seconds
                xaxis: str
                    Can be `period` or `frequency` depending what on the type of plot
                display: str
                    `On` or `Off` to display image
                folder out: str
                    Path to save the output 

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].WaveAnalysis.wave_spectra(sea_level='ssh',args={'windows:3600,'nfft':3600,'overlap':3600)
            >>> 
        """

        unit=get_opt(self.data[sea_level],'units',args.get('units','m'))
        display=True
        if args.get('display','Off')=='Off':
            display=False

        detrend=False
        if args.get('detrend',False)=='linear':
            detrend='linear'
        elif args.get('detrend',False)== 'constant':
            detrend='constant'


        Xaxis=True
        if args.get('xaxis','period')=='period':
            Xaxis=False

        if not hasattr(self.data,'filename'):
            self.data.filename=''

        filename=os.path.join(args.get('folder out',os.getcwd()),os.path.splitext(self.data.filename)[0]+'_Spec.png')
        error=do_wave_spectra_plot(self.data.index,self.data[sea_level].values,unit,
            args.get('windows',3600),
            args.get('overlap',1800),
            args.get('nfft',3600),
            detrend,args.get('period (s) min and max for plotting',[10,1000]),Xaxis,filename,display)


    def ssh_to_wave(self,sea_level='sea_level',\
        args={
         'windows': 3600,
         'overlap':1800,
         'nfft':3600,
         'detrend':{'Off':True,'linear':False,'constante':False},
         'wave period range (min and max) (in s)':[3, 25],
         'method':{'spectra':True,'zero-crossing':False},
         'minimum number of waves per window for zero crossing analysis': 30,
         'crossing':{'downcrossing':True,'upcrossing':False},
         }):
        

        """ This function transform a timeseries of elevation to Hs using:
            -Spectra method
            - zero-crossing method

            Parameters
            ~~~~~~~~~~

            sea_level : str
                Name of the column which contains the sea level.
            args: dict
                Dictionnary with the folowing keys:
                units: str
                    Units of the sea level
                windows: int
                    windows to process in seconds.
                overlap: int
                    overlap in seconds
                nfft: int
                     Length of the signal to calculate the Fourier transform of.
                detrend: str
                    `linear`, `constante` or `Off` to detrend the timeseries before doing the analysis
                wave period range (min and max) (in s): list
                    Calulating wave within this Wave period
                method: str
                    Can be `spectra` or `zero-crossing` depending what method to use
                minimum number of waves per window for zero crossing analysis: int
                    Minimum number of waves per window for zero crossing analysis
                crossing: str
                    Can be `downcrossing` or `upcrossing`. Method to use if not using the spectra method

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].WaveAnalysis.ssh_to_wave(sea_level='ssh',args={'method'='spectra',windows:3600,'nfft':3600,'overlap':3600)
            >>> 
        """
        min_wave=args.get('minimum number of waves per window for zero crossing analysis',30)
        period=args.get('wave period range (min and max) (in s)',[3, 25])
        method=args.get('method','zero-crossing')
        if method=='zero-crossing':
            self.data[sea_level]=bandpass_filter(self.data[sea_level],args={'lower cut-off (s)':period[0],'upper cut-off (s)':period[1]})




        detrend=False
        if args.get('detrend',False)=='linear':
            detrend='linear'
        elif args.get('detrend',False)== 'constant':
            detrend='constant'

        crossing=False
        if args.get('crossing',False)=='upcrossing':
            crossing=True

        self.dfout=do_ssh_to_wave(self.data.index,self.data[sea_level].values,
            args.get('overlap',3600),
            args.get('nfft',3600),args.get('windows',3600),detrend,period,min_wave,crossing,method)

        self.dfout.index.name='time'

        return self.dfout


    def wavelet_analysis(self,sea_level='sea_level',\
        args={
         'units':'m',
         'mother wavelet':{'Morlet':True,'Paul':False,'DOG':False},
         'wave period range (min and max) (in s)':[3, 25],
         'number of sub-ocatve per period band': 8,
         'folder out':os.getcwd(),
         'display':{'On':True,'Off':False}
         }):
        

        """ This function estimates the wavelet power spectrum of a time series, as
            well as the scaled-averaged wavelet power time series within a specific
            period band. The code is based on the wavelet toolbox from Torrence and
            Compo
            See https://paos.colorado.edu/research/wavelets/software.html

            Parameters
            ~~~~~~~~~~

            sea_level : str
                Name of the column which contains the sea level.
            args: dict
                Dictionnary with the folowing keys:
                units: str
                    Units of the sea level
                mother wavelet: str
                    Can be `Morlet`,`Paul` or `DOG`
                wave period range (min and max) (in s): list
                    Calulating wave within this Wave period
                number of sub-ocatve per period band: int
                     Number of sub-ocatve per period band
                display: str
                    `On` or `Off` to display image
                folder out: str
                    Path to save the output 

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].WaveAnalysis.wavelet_analysis(sea_level='ssh',args={})
            >>> 
        """

        display=True
        if args.get('display','Off')=='Off':
            display=False

        if not hasattr(self.data,'filename'):
            self.data.filename=''

        filename=os.path.join(args.get('folder out',os.getcwd()),os.path.splitext(self.data.filename)[0]+'_Wavelet.png')
        period=args.get('wave period range (min and max) (in s)',[3,25])


        unit=get_opt(self.data[sea_level],'units',args.get('units','m'))

        do_wavelet(self.data.index,self.data[sea_level],
            args.get('mother wavelet','Morlet'),period,args.get('number of sub-ocatve per period band',8),
            unit,filename,display)