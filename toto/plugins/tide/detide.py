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
    def _export_cons(self,outfile,var,cons,amp,pha):

        mat=[]
        row=['Constituent','Amplitude [m]','Phase [deg]']
        mat.append(row)
        for i,con in enumerate(cons):
            row=[con]
            row.append('%.2f' %amp[i])
            row.append('%.2f' %pha[i])
            mat.append(row)

        create_table(outfile,var,np.array(mat))

    def detide(self,mag='mag',\
        args={'Minimum SNR':2,\
        'Latitude':-36.0,
        'folder out':os.getcwd(),
        }):

        """ This function detide a timeseries.
        Works if NaN are in the timeseries"""

        if hasattr(self.data,'latitude'):
            latitude=self.data.latitude[0]
            if not latitude:
                latitude=args['Latitude']
        else:
            latitude=args['Latitude']
        if hasattr(self.data[mag],'short_name'):
            short_name=self.data[mag].short_name
        else:
            short_name=mag
            
        time=self.data.index
        dt=(time[2]-time[1]).total_seconds()/3600 # in hours
        stime=np.array(date2num(time))
        lat=latitude
        if hasattr(self.data,'filename'):
            outfile=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'_Conc.xlsx')
        else:
            outfile=os.path.join(args['folder out'],'Conc.xlsx')

        ray=args['Minimum SNR']
        demeaned = self.data[mag].values - np.nanmean(self.data[mag].values)

        opts = dict(method='ols',conf_int='linear', Rayleigh_min=ray)
        coef = solve(stime,demeaned,lat= lat,**opts)
        ts_recon = reconstruct(stime, coef).h

        self.dfout[short_name+'t']=ts_recon
        self.dfout[short_name+'o']=demeaned-ts_recon

        self._export_cons(outfile,short_name,coef['name'],coef['A'],coef['g'])
        
        return self.dfout

    def recreate(self,\
        args={'cons file':os.path.join(os.getcwd(),'cons_list.txt'),\
        'column cons': 'cons',
        'column amp': 'amp',
        'column pha': 'pha',
        'minimum time':datetime.now(),'maximum time':datetime.now()+timedelta(days=7),'dt(s)':3600,
        'Latitude':-36.0,
        }):

        # if not os.pagth.isfile(args['cons file']):
        #     print('Can''t find file: %s' % args['cons file'])

        # try:
        df = pd.read_csv(args['cons file'])
        # except:
        #     print('Can''t read file with pandas.read_csv')
        #     return

        # if (args['column cons'] or args['column amp'] or args['column pha']) not in df:
        #     print('Can''t find the columns')
        #     return       

        constituents=df[args['column cons']].values
        amplitudes=df[args['column amp']].values
        phases=df[args['column pha']].values


        latitude=args['Latitude']

        min_time=args['minimum time']
        max_time=args['maximum time']
        min_dt=args['dt(s)']


        idx = pd.period_range(args['minimum time'], args['maximum time'],freq='%is'%args['dt(s)'])
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

        self.dfout=df_new#pd.merge_asof(self.dfout,df_new,on='time',direction='nearest', tolerance=pd.Timedelta("1s")).set_index('time')
        self.dfout.index.name='time' 
        return self.dfout
    def predict(self,mag='mag',\
        args={'minimum time':datetime,'maximum time':datetime,'dt(s)':60,'Minimum SNR':2,\
        'Latitude':-36.0,
        }):

        """ This function predict the tide by first detiding a timeseries.
        Works if NaN are in the timeseries"""

        if hasattr(self.data,'latitude'):
            latitude=self.data.latitude[0]
            if not self.data.latitude:
                latitude=args['Latitude']
        else:
            latitude=args['Latitude']

        time=self.data.index
        dt=(time[2]-time[1]).total_seconds()/3600. # in hours
        stime=np.array(date2num(time))
        lat=latitude
        ray=args['Minimum SNR']
        demeaned = self.data[mag].values - np.nanmean(self.data[mag].values)
        opts = dict(method='ols',conf_int='linear', trend=False, Rayleigh_min=ray)
        coef = solve(stime,demeaned,lat= lat,**opts)


        min_time=min(args['minimum time'],time[0])
        max_time=max(args['maximum time'],time[-1])
        min_dt=args['dt(s)']


        idx = pd.period_range(args['minimum time'], args['maximum time'],freq='%is'%args['dt(s)'])
        idx=idx.to_timestamp()
        df_new=pd.DataFrame(index=idx)

        if hasattr(self.data[mag],'short_name'):
            short_name=self.data[mag].short_name
        else:
            short_name=mag

        df_new[short_name+'t'] = reconstruct(np.array(date2num(df_new.index)), coef).h
        df_new.index.name='time'
        
        self.dfout=df_new#pd.merge_asof(self.dfout,df_new,on='time',direction='nearest', tolerance=pd.Timedelta("1s")).set_index('time')
        self.dfout.index.name='time' 


        return self.dfout


    def tidal_stat(self,mag='mag',\
        args={'Minimum SNR':2,\
        'Latitude':-36.0,
        'folder out':os.getcwd(),
        }):

        '''Function to extract the tide stats from a time series
            i.e HAT,LAT,MHWS,MLWS...'''

        if hasattr(self.data,'latitude'):
            latitude=self.data.latitude
            if not self.data.latitude:
                latitude=args['Latitude']
        else:
            latitude=args['Latitude']

        time=self.data.index
        dt=(time[2]-time[1]).total_seconds()/3600 # in hours
        stime=np.array(date2num(time))
        lat=latitude
        ray=args['Minimum SNR']
        demeaned = self.data[mag].values - np.nanmean(self.data[mag].values)
        opts = dict(method='ols',conf_int='linear', Rayleigh_min=ray)
        coef = solve(stime,demeaned,lat= lat,**opts)
        m2=(coef.name=='M2').nonzero()[0][0]
        s2=(coef.name=='S2').nonzero()[0][0]
        rpd = np.pi/180
        M2 = coef['A'][m2] 
        S2 = coef['A'][s2]
        t = pd.date_range(start='2000-01-01', periods=24*365*20, freq='H')
        time = date2num(t.to_pydatetime())
        ts_recon = reconstruct(time, coef).h

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
        stats[1,2]='%.2f' % (max(ts_recon))
        stats[2,2]='%.2f' % (M2+S2)
        stats[3,2]='%.2f' % (M2-S2)
        stats[4,2]='%.2f' % (0)
        stats[5,2]='%.2f' % (-M2+S2)
        stats[6,2]='%.2f' % (-M2-S2)
        stats[7,2]='%.2f' % (min(ts_recon))

        if hasattr(self.data,'filename'):
            outfile=os.path.join(args['folder out'],os.path.splitext(self.data.filename)[0]+'_Concstats.xlsx')
        else:
            outfile=os.path.join(args['folder out'],'Concstats.xlsx')
        create_table(outfile,'stat',stats)

    def skew_surge(self,mag='mag',args={'Minimum SNR':2,\
        'Latitude':-36.0}):
        #

        """ This function calculate the skew surge :
        see https://www.ntslf.org/storm-surges/skew-surges"""

        if hasattr(self.data,'latitude'):
            latitude=self.data.latitude
            if not self.data.latitude:
                latitude=args['Latitude']
        else:
            latitude=args['Latitude']

        xobs=self.data.index
        dt=(xobs[2]-xobs[1]).total_seconds()/3600. # in hours
        stime=np.array(date2num(xobs))
        lat=latitude
        ray=args['Minimum SNR']
        yobs = self.data[mag].values - np.nanmean(self.data[mag].values)
        opts = dict(method='ols',conf_int='linear', Rayleigh_min=ray)
        coef = solve(stime,yobs,lat= lat,**opts)


        min_time=xobs[0]
        max_time=xobs[-1]
        min_dt=15*60


        xpredi = pd.period_range(min_time, max_time,freq='%is'%min_dt)
        xpredi=xpredi.to_timestamp()

        if hasattr(self.data[mag],'short_name'):
            short_name=self.data[mag].short_name
        else:
            short_name=mag

        ypredi = reconstruct(np.array(date2num(xpredi)), coef).h


        pe,tr=peaks(ypredi)

        df_new=pd.DataFrame(index=xobs)
        skew=copy.deepcopy(yobs)
        skew[:]=np.nan
                
        for i in range(0,len(tr)-1):
            idx_pred=np.logical_and(xpredi>xpredi[tr[i]],xpredi<xpredi[tr[i+1]])
            idx_obs=np.logical_and(xobs>xpredi[tr[i]],xobs<xpredi[tr[i+1]])

            max_pre=np.max(ypredi[idx_pred])
            max_obs=np.max(yobs[idx_obs])
            max_obs_idx=np.argmax(yobs[idx_obs])
            skew[idx_obs.nonzero()[0][max_obs_idx]]=max_obs-max_pre

        df_new['skew_surge']=skew


        return df_new.dropna()
