import numpy as np
from scipy.interpolate import interp1d
from scipy import signal
from itertools import groupby
from toto.core.wavestats import specstats
from matplotlib.dates import date2num
import pandas as pd

def zerodn(time,mag,Upcross=False):

    # normalize elevation
    mag -= np.mean(mag)
    time=date2num(time)

    # Number of crests:
    dfy = np.diff(mag)
    dfyb = np.concatenate((dfy,[0]))
    dfyf = np.concatenate(([0],dfy))
    Ncrests = sum((dfyb<0) & (dfyf>0))

    sy = np.sign(mag)
    dsy = .5*np.diff(sy)
    if Upcross:
        dsy=dsy*-1

    dcinds = np.concatenate(([0],dsy))
    dcinde = np.concatenate((dsy, [0]))
    cs = np.cumsum(dcinds == -1)
    ys = mag[dcinds == -1]
    ye = mag[dcinde == -1]
    ts = time[dcinds == -1]
    te = time[dcinde == -1]
    Nz = len(ys)
    if len(ye) != Nz | len(ts) != Nz | len(te) != Nz:
        assert 'zerodn: Inconsistent number of zero-crossing periods'


    if Nz <= 1:
        return None

    ydiff = ys - ye
    ts =  (te*ys - ts*ye)/ydiff
    Stime = ts[:Nz-1]
    Etime = ts[1:Nz]
    Htime = .5*(Stime + Etime)
    Period = np.diff(ts)
    Nz = Nz - 1;

    Ht = np.zeros((Nz,))

    for k in range(0,Nz):
      ysub = mag[cs == k]
      Ht[k] = max(ysub) - min(ysub)

    return Ht,Period
    
def get_stats(Ht,Period,min_n=30):
    stat={}
    stat['hs']=np.NaN
    stat['ts']=np.NaN
    stat['hmax']=np.NaN
    stat['tmax']=np.NaN
    stat['h10']=np.NaN
    stat['t10']=np.NaN

    gd=~np.isnan(Ht)
    Ht=Ht[gd]
    Period=Period[gd]

    if len(Ht)>=min_n:
        n=len(Ht)
        idx=np.argsort(Ht)
        P=Period[idx]
        H=Ht[idx]
        s=int(round(n*2/3))
        s10=int(round(n*9/10))
        stat['hs'] = np.mean(H[s:]);
        stat['ts'] = np.mean(P[s:]);

        stat['hmax'] = H[-1]
        stat['tmax'] = P[-1]

        stat['h10'] = np.mean(H[s10:])
        stat['t10'] = np.mean(P[s10:])


    return stat


def zero_crossing(df,itime,time,mag,Upcross,min_n):

    Ht,Period=zerodn(time,mag,Upcross)
    WB=get_stats(Ht,Period*3600*24,min_n)
    df0=pd.DataFrame(WB,index=[itime])

    df=df.append(df0)
    return df


def spectra_analysis(df,time,mag,sint,window,overlap,fft,detrend,Tmin,Tmax):
    freqs, psd = signal.welch(mag,fs=1./sint,nperseg=window,noverlap=overlap,nfft=fft,detrend=detrend)
    WB=specstats(psd,freqs,fmin=1/Tmax,fmax=1/Tmin,cutoff=1/8)
    
    df0=pd.DataFrame(WB['tot'],index=time)
    tmp=pd.DataFrame(WB['sw'],index=time).add_suffix('_sw')
    df0=df0.merge(tmp,left_index=True,right_index=True)
    tmp=pd.DataFrame(WB['sea'],index=time).add_suffix('_sea')
    df0=df0.merge(tmp,left_index=True,right_index=True)
    df=df.append(df0)

    return df

def do_ssh_to_wave(time,mag,noverlap,nfft,nperseg,detrend,period,min_wave,crossing,method):


    sint=(time[2]-time[1]).total_seconds()
    Tmin=period[0]
    Tmax=period[1]
    if period[0] <= 1.9999*sint:
        return print('The minimum analysed period must be at least twice the sampling period (i.e. >= '+str(2*sint)+' s)')


    if period[1] > nfft*sint:
        return print('The minimum window and nfft length must be larger than the maximum plotting period (i.e. window >= '+str(np.round(Tmax/sint))+' and nfft > '+str(np.round(Tmax/sint))+')')

    # bad=np.isnan(mag)
    # mag=mag[~bad] #removes possible NaN on the edges of the time series


    #convert window and overlap in number of time steps
    overlap_H=noverlap/3600
    window = int(nperseg/sint)
    overlap = int(noverlap/sint)
    fft=int(nfft/sint)
    


    #start at the first fix hour
    
    MM=time.minute+time.second/60.
    HH=time.hour+MM/60.
    #make sure we start the time series at the right time in order to have
    #windows centred on the hour,30min,15min etc...
    start=0

    if overlap_H>=1:
        x=np.isin(HH, np.arange(0,24,overlap_H)).nonzero()[0]
        start=x[0]
        i=0
        while start<0:
            start=int(x[i]-np.round(window/2))
            i+=1
    else:
        overlap_M=overlap_H*60 #convert to min
        x=np.isin(MM, np.arange(0,60,overlap_M)).nonzero()[0]
        start=x[0]
        while start<0:
            start=int(x[i]-np.round(window/2))


    mag=mag[start:]
    time=time[start:]
    df=pd.DataFrame()
    for i in range(0,len(mag)-window,overlap):
        if i % 10000 ==0:
            print('==>%i/%i'%(i,len(mag)-window))
        data =mag[i:i+window]
        N=len(data);
        t=time[i:i+window]
        #%%%%%%%%%%%%%identify the length of NaN blocks
        a=np.isnan(data).astype(int)
        nan_block_length=[sum(1 for i in g) for k,g in groupby(a) if k==1]

        #%%%%%%%%%%%%%%%%%do spectrum analysis
        if  len(a[a==1]) < N/2: #& len((nan_block_length>Tmin/sint).nonzero()[0]) < 4: 
                #set_interp = interp1d(t[~np.isnan(data)], data[~np.isnan(data)])
                #data=set_interp(t) #removes NaN
                #data=data[~np.isnan(data)] #removes possible NaN on the edges of the time series 
                if method=='spectra':         
                    df=spectra_analysis(df,[time[i+int(window/2)]],data,sint,window,overlap,fft,detrend,Tmin,Tmax)
                else:
                    df=zero_crossing(df,time[i+int(window/2)],t,data,crossing,min_wave)


    return df


