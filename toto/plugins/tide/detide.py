from utide import solve,reconstruct,ut_constants,utilities
import pandas as pd
import os
from ...core.make_table import create_table
import numpy as np
from matplotlib.dates import date2num,num2date 
from datetime import datetime,date,timedelta
from ...core.make_table import create_table
import copy
from ...core.toolbox import peaks



@pd.api.extensions.register_dataframe_accessor("TideAnalysis")
class TideAnalysis:
    def __init__(self, pandas_obj):
#        self._validate(pandas_obj)
        self.data = pandas_obj
        self.dfout = pd.DataFrame(index=self.data.index.copy())
        self.constituents = None

    def _cons2ts(min_time,max_time,dt,constituents,amplitudes,phases,latitude):

        idx = pd.period_range(min_time, max_time,freq='%is'%dt)
        idx=idx.to_timestamp()
        df_new=pd.DataFrame(index=idx)

        const_idx = np.asarray([ut_constants['const']['name'].tolist().index(i) for i in constituents])
        frq = ut_constants['const']['freq'][const_idx]

        coef = utilities.Bunch(name=constituents, mean=0, slope=0)
        coef['aux'] = utilities.Bunch(reftime=729572.47916666674, lind=const_idx, frq=frq)
        coef['aux']['opt'] = utilities.Bunch(twodim=False, nodsatlint=False, nodsatnone=False,nodiagn=True,
                                   gwchlint=False, gwchnone=False, notrend=True, prefilt=[])

        # Prepare the time data for predicting the time series. UTide needs MATLAB times.
        times = date2num(df_new.index)


        coef['aux']['lat'] = latitude  # float
        coef['A'] = amplitudes
        coef['g'] = phases
        coef['A_ci'] = np.zeros(amplitudes.shape)
        coef['g_ci'] = np.zeros(phases.shape)
        df_new['tide'] = reconstruct(times, coef, verbose=True).h

        return df_new

    def _export_cons(self,outfile,var,cons,amp,pha):

        mat=[['Constituent','Amplitude [m]','Phase [deg]']]
        for i,con in enumerate(cons):
            row=[con]
            row.append('%.4f' %amp[i])
            row.append('%.4f' %pha[i])
            mat.append(row)

        create_table(outfile,var,np.array(mat))

    def get_constituents(self, constituents=None):

        # If no constituents provided use precomputed ones if available
        if constituents is None:
            if self.constituents is None:
                print("No constituents available in Tide Analysis object please provide constituents")
                raise
            print("Using pre-computed constituents from TideAnalysis object")
            constituents = self.constituents
        return constituents


    def fit_tides(self,
                  mag='mag',
                  args={'minimum SNR':2,
                        'latitude':-36.0,
                        'method': 'ols',
                        'conf_int': 'linear',
                        'trend': True
                  }):

        # Parse latitude
        if hasattr(self.data,'latitude'):
            try:
                latitude=self.data.latitude[0]
                if not latitude:
                    latitude=args.pop('latitude')
            except:
                    latitude=args.pop('latitude')
        else:
            latitude=args.pop('latitude')

        # Center timeseries around mean
        demeaned = self.data[mag].values - np.nanmean(self.data[mag].values)

        # Parse and set options for the tidal analysis
        # if those have not already been defined
        for key,value in dict(method = args.get('method', 'ols'),
                              conf_int = args.get('conf_int', 'linear'),
                              trend = args.get('trend', False),
                              Rayleigh_min = args.get('minimum SNR',2)).items():
            if not key in args:
                args[key] = value

        # This is because the key gets renamed to "Rayleigh_min"
        if 'minimum SNR' in args:
            args.pop('minimum SNR')


        # Fit the tides and get the constituents
        self.constituents = solve(np.array(date2num(self.data.index)),
                                  demeaned,
                                  lat= latitude,
                                  **args)

        return self.constituents


    def tidal_elevation_from_constituents(self,
                                          constituents=None,
                                          time=None,
                                          tstart=None, tend=None, dt=None):

        # If no time provided use same as analyses dataset
        # Generate times of time-series
        if time is None:
            if not tstart is None or not tend is None or not dt is None:
                if tstart is None or tend is None or dt is None:
                    print("Please supply all (tstart, tend, dt)")
                    raise
                time = pd.period_range(tstart, tend, freq=dt).to_timestamp()
            else:
                time = self.data.index
        else:
            if not tstart is None or not tend is None or not dt is None:
                print("Please supply either time or (tstart, tend, dt)")
                raise

        # Parse constituents attribute and get them if available
        constituents = self.get_constituents(constituents=constituents)

        # Reconstructe elevation timeseries from constituents
        tide_elevation = reconstruct(np.array(date2num(time)),
                                     constituents).h

        # Store it in a pandas dataframe
        out = pd.DataFrame({'tidal_elevation': tide_elevation},
                            index=time)

        # Make sure the index is labelled as 'time'
        out.index.name = 'time'

        return out


    def write_constituents_to_file(self,
                                   filename):
        pass


    def load_constituents_from_file(self,
                                    filename):
        pass


    def detide(self,
               constituents=None,
               mag='mag',
               args={'minimum SNR':2,
                     'latitude':-36.0,
                     'folder out':os.getcwd()}):

        """ This function detide a timeseries using Utide software.
        Usefull if NaNs are in the timeseries

        Parameters
        ~~~~~~~~~~

        mag : str
            Name of the column from which to extract the tide
        args: dict
            Dictionnary with the folowing keys:
                minimum SNR: int
                folder out: str
                    Path to save the output
                latitude: float

        Examples:
        ~~~~~~~~~
        >>> df=tf['test1']['dataframe'].TideAnalysis.detide(mag='U',args={'latitude':-36.5})
        >>>
        """

        # Parse output folder
        # This should ideally be somewhere else in the interface than in args
        # but accomodating here to ensure backward compatibility
        folder_out = args.pop('folder out') if 'folder out' in args else os.getcwd()

        # Centre time-series around mean
        demeaned = self.data[mag].values - np.nanmean(self.data[mag].values)

        # Fit tides to get tidal constituents if not provided
        if constituents is None:
            constituents = self.fit_tides(mag=mag,
                                          args=args)

        # Reconstuction astronomical tide time-series from coefficients
        ts_recon = self.tidal_elevation_from_constituents(constituents=constituents,
                                                          time=self.data.index)

        # Pack results in a dataframe with names defined from the raw data base name
        if hasattr(self.data[mag],'short_name'):
            short_name=self.data[mag].short_name
        else:
            short_name=mag

        dfout = ts_recon.rename(columns={'tidal_elevation': short_name+'t'})
        dfout[short_name+'o'] = demeaned - dfout[short_name+'t']

        # Output constituents to file
        if hasattr(self.data,'filename'):
            outfile=os.path.join(folder_out,
                                 os.path.splitext(self.data.filename)[0]+'_Conc.xlsx')
        else:
            outfile=os.path.join(folder_out,
                                 'Conc.xlsx')

        # Store constituents in output file
        self._export_cons(outfile,
                          short_name,
                          constituents['name'],
                          constituents['A'],
                          constituents['g'])

        return dfout

    def recreate(self,
        args={'cons file':os.path.join(os.getcwd(),'cons_list.txt'),
        'column cons': 'cons',
        'column amp': 'amp',
        'column pha': 'pha',
        'minimum time':datetime.now(),
        'maximum time':datetime.now()+timedelta(days=7),
        'dt(s)':3600,
        'latitude':-36.0,
        }):

        """ Re-create a time series using a file containing
         Amplitude and Phase for each contituents.

        Parameters
        ~~~~~~~~~~

        args: dict
            Dictionnary with the folowing keys:
                cons file: str
                    Txt file containing the amplitude and phase
                column cons: str
                    Name of the column containing the constituent name
                column amp: str
                    Name of the column containing the constituent amplitude
                column pha: str
                    Name of the column containing the constituent phase (in degree)
                minimum time: datetime
                    Time the time series start
                maximum time: datetime
                    Time the time series end
                dt(s): int
                   Time interval in seconds
                latitude: float

        Examples:
        ~~~~~~~~~
        >>> df=tf['test1']['dataframe'].TideAnalysis.recreate(args={'cons file':'test.txt',\
        'column cons':'cons','column amp':amp,'column pha':pha,\
        'minimum time':datetime.datetime(2002,1,1),'maximum time':datetime.datetime(2003,1,1),\
        'dt(s)':3600,'latitude':-36)
        >>>
        """

        # Read constituents csv file
        df = pd.read_csv(args['cons file'])

        # Order constituents information
        constituents = df[args['column cons']].values
        amplitudes = df[args['column amp']].values
        phases = df[args['column pha']].values

        # Parse latitude information
        latitude=args['latitude']

        # Parse info on the times the time-series of tidal elevation has to be generated for
        min_time=args['minimum time']
        max_time=args['maximum time']
        dt=args['dt(s)']

        # Reconstruct the time-series of water elevation
        df_new=self._cons2ts(min_time,max_time,dt,constituents,amplitudes,phases,latitude)


        # Store as dataframe and return
        self.dfout=df_new#pd.merge_asof(self.dfout,df_new,on='time',direction='nearest', tolerance=pd.Timedelta("1s")).set_index\('time')
        self.dfout.index.name='time'
        return self.dfout


    def predict(self,
                mag='mag',
                args={'minimum time':datetime,'maximum time':datetime,'dt(s)':60,
                      'minimum SNR':2,'trend': False,
                      'latitude':-36.0,
                },
                constituents=None):

        """ This function predict the tide by first detiding a timeseries.
        Works if NaN are in the timeseries

        Parameters
        ~~~~~~~~~~

        mag : str
            Name of the column from which to extract the tide
        args: dict
            Dictionnary with the folowing keys:
                minimum SNR: int
                folder out: str
                   Path to save the output
                latitude: float
                minimum time: datetime
                    Time the time series start
                maximum time: datetime
                    Time the time series end
                dt(s): int
                    Time interval in seconds

        Examples:
        ~~~~~~~~~
        >>> df=tf['test1']['dataframe'].TideAnalysis.predict(mag='U',args={'latitude':-36.5,\
            'minimum time':datetime.datetime(2002,1,1),'maximum time':datetime.datetime(2003,1,1),\
            'dt(s)':3600)
        >>>
        """

        # Parse out of args anything not related to tides
        # ideally this separation should be respected in the function interface
        # but we won't do that right now for backward compatibility reasons
        # I dont' think the folder out option in the doc is of any relevance here
        minimum_time = args.pop('minimum time')
        maximum_time = args.pop('maximum time')
        min_dt = args.pop('dt(s)')

        # Fit tides to get constituents if not provided
        if constituents is None:
            print("Using TideAnalysis constituents if available")
            constituents = self.fit_tides(mag=mag,
                                          args=args)

        # Parse info on the times the time-series of tidal elevation has to be generated for
        min_time = min(minimum_time, time[0])
        max_time = max(maximum_time, time[-1])

        # Generate times of time-series
        idx = pd.period_range(minimum_time, maximum_time,freq='%is'%min_dt)
        idx = idx.to_timestamp()

        # Get tidal elevation time-series for times
        dfout = self.tidal_elevation_from_constituents(idx, constituents)

        # Rename variable to maintain backward compatibiity
        dfout = dfout.rename(colums={'tidal_elevation': self.get_default_name()})
        self.dfout = dfout

        return dfout


    def get_default_name(self):
        """
        Function that returns the default name for a time series of reconstructed
        astronomical tidal water level.
        """

        if hasattr(self.data[mag], 'short_name'):
            return self.data[mag].short_name+'t'
        else:
            return mag+'t'


    def tidal_stat(self,
                   constituents=None,
                   mag='mag',
        args={'minimum SNR':2,
        'latitude':-36.0,
        'folder out':os.getcwd(),
        }):

        """Function to extract the tide stats from a time series
            i.e HAT,LAT,MHWS,MLWS...

        Parameters
        ~~~~~~~~~~

        mag : str
            Name of the column from which to extract the tide
        args: dict
            Dictionnary with the folowing keys:
                minimum SNR: int
                folder out: str
                    Path to save the output
                latitude: float

        Examples:
        ~~~~~~~~~
        >>> df=tf['test1']['dataframe'].TideAnalysis.tidal_stat(mag='U',args={'latitude':-36.5})
        >>>
        """

        # Parse output folder
        # This should ideally be somewhere else in the interface than in args
        # but accomodating here to ensure backward compatibility
        folder_out = args.pop('folder out') if 'folder out' in args else os.getcwd()

        if constituents is None:
            constituents = self.fit_tides(mag=mag,
                                          args=args)

        m2=(constituents.name=='M2').nonzero()[0][0]
        s2=(constituents.name=='S2').nonzero()[0][0]
        rpd = np.pi/180
        M2 = constituents['A'][m2]
        S2 = constituents['A'][s2]
        t = pd.date_range(start='2000-01-01', periods=24*365*20, freq='H')
        time = date2num(t.to_pydatetime())
        #ts_recon = reconstruct(time, coef).h
        ts_recon = self.tidal_elevation_from_constituents(constituents=constituents,
                                                          time=time)

        stats=np.empty((8,3),dtype="object")
        stats[0,0]='Parameter'
        stats[1,0]='HAT'
        stats[2,0]='MHWS'
        stats[3,0]='MHWN'
        stats[4,0]='MSL'
        stats[5,0]='MLWN'
        stats[6,0]='MLWS'
        stats[7,0]='LAT'

        stats[0,1]='Description'
        stats[1,1]='Highest Astronomical Tide'
        stats[2,1]='Mean High Water Springs (M2+S2)'
        stats[3,1]='Mean High Water Neaps (M2-S2)'
        stats[4,1]='Mean Sea Level'
        stats[5,1]='Mean Low Water Neaps (-M2+S2)'
        stats[6,1]='Mean Low Water Springs (-M2-S2)'
        stats[7,1]='Lowest Astronomical Tide'


        stats[0,2]='Elevation (m), relative to MSL';
        #stats[1,2]='%.2f' % (max(ts_recon))
        stats[1,2]='%.2f' % (ts_recon['tidal_elevation'].max())
        stats[2,2]='%.2f' % (M2+S2)
        stats[3,2]='%.2f' % (M2-S2)
        stats[4,2]='%.2f' % (0)
        stats[5,2]='%.2f' % (-M2+S2)
        stats[6,2]='%.2f' % (-M2-S2)
        #stats[7,2]='%.2f' % (min(ts_recon))
        stats[7,2]='%.2f' % (ts_recon['tidal_elevation'].min())

        if hasattr(self.data,'filename'):
            outfile=os.path.join(folder_out,os.path.splitext(self.data.filename)[0]+'_Concstats.xlsx')
        else:
            outfile=os.path.join(folder_out,'Concstats.xlsx')
        create_table(outfile,'stat',stats)

        return stats


    def skew_surge(self,
                   constituents=None,
                   tide_dt=900,
                   mag='mag',
                   args={'minimum SNR':2,
                        'latitude':-36.0}):
        """ This function calculate the skew surge :
        see https://www.ntslf.org/storm-surges/skew-surges

        Parameters
        ~~~~~~~~~~
        constituents: object
            Tidal constituents to use to estimate the astronomical tides. Get calculated
            if not supplied.
        tide_dt: int
             Time delta to use to reconstruct the astronomical tides in seconds. Default is
             15 minutes.
        mag : str
            Name of the column from which to extract the tide.
        args: dict
            Dictionnary with the parameters to use to fit the tides if required:
                minimum SNR: int
                latitude: float

        Examples:
        ~~~~~~~~~
        >>> df=tf['test1']['dataframe'].TideAnalysis.skew_surge(mag='U',args={'latitude':-36.5})
        >>>
        """

        # Total water level time-series is the base data re-centered around the mean
        xtwl = self.data.index
        ytwl = self.data[mag].values - np.nanmean(self.data[mag].values)

        # Fit tides if constituents are not already provided
        if constituents is None:
            constituents = self.fit_tides(mag=mag, args=args)

        # Generate times over which the astronomical tide needs reconstructing
        xtide = pd.period_range(xtwl[0], xtwl[-1], freq='%is'%(tide_dt))
        xtide = xtide.to_timestamp()

        # Reconstruct the astronomical tides
        ytide = self.tidal_elevation_from_constituents(constituents=constituents,
                                                        time=xtide)['tidal_elevation'].values

        # Find peaks in tide
        pe,tr = peaks(ytide)

        # Create arrays to store results
        skew = copy.deepcopy(ytwl)
        skew_lag = copy.deepcopy(ytwl)
        ytwl_max = copy.deepcopy(ytwl)
        xtide_max = copy.deepcopy(ytwl).astype(datetime)
        ytide_max = copy.deepcopy(ytwl)
        skew[:] = np.nan
        skew_lag[:] = np.nan
        ytwl_max[:] = np.nan
        xtide_max[:] = np.nan
        ytide_max[:] = np.nan

        # Loop over peaks in tide (tidal cycles)
        for i in range(0,len(tr)-1):
            # Extract astronomical tide and total water level data for cycle
            idx_tide=np.logical_and(xtide>xtide[tr[i]],xtide<xtide[tr[i+1]])
            idx_twl=np.logical_and(xtwl>xtide[tr[i]],xtwl<xtide[tr[i+1]])

            # Find maxima position in both time-series for tidal cycle
            max_tide_idx = np.argmax(ytide[idx_tide])
            max_twl_idx = np.argmax(ytwl[idx_twl])

            # Get maxima value in both time-series for tidal cycle
            max_tide = ytide[idx_tide][max_tide_idx]
            max_twl = ytwl[idx_twl][max_twl_idx]

            # Turn maxima position in tidal cycle in maxima position in total timeseries
            total_max_tide_idx = idx_tide.nonzero()[0][max_tide_idx]
            total_max_twl_idx = idx_twl.nonzero()[0][max_twl_idx]

            # Calculate skew surge and lag (in hours)
            skew[total_max_twl_idx] = max_twl - max_tide
            skew_lag[total_max_twl_idx] =            (xtide[total_max_tide_idx] - xtwl[total_max_twl_idx]) / np.timedelta64(1, 'h')

            ytide_max[total_max_twl_idx] = max_tide
            xtide_max[total_max_twl_idx] = xtide[total_max_tide_idx]
            ytwl_max[total_max_twl_idx] = max_twl

        # Fit all results in a dataframe and return
        dout = pd.DataFrame({'skew_surge_magnitude': skew,
                             'skew_surge_lag': skew_lag,
                             'tidal_elevation_maximum_over_tidal_cycle': ytide_max,
                             'tidal_elevation_maximum_time_over_tidal_cycle': xtide_max,
                             'total_water_level_maximum_over_tidal_cycle': ytwl_max
                             },
                            index=xtwl).dropna()
        dout.index.name = 'time'

        return dout
