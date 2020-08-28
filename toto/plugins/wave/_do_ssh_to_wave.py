import numpy as np
from scipy.interpolate import interp1d
from scipy import signal
from itertools import groupby
from toto.core.wavestats import specstats
import pandas as pd


def zero_crossing(df,time,mag,sint):
    import pdb;pdb.set_trace()
    # [Ht,Period] = zerodn(data,t,[],cross);
    # if length(Ht)> min_number_waves
    #         [hs(n),hmax(n),h10(n),ts(n),tmax(n),t10(n)] = Wave_stats(Ht,Period*24*3600);%period in s
    #         tm(n) = nanmean(Period*24*3600);
    # else




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

def do_ssh_to_wave(time,mag,noverlap,nfft,nperseg,detrend,period,min_wave,method='spectra'):

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
        if i % 100000 ==0:
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
                    df=spectra_analysis(df,[time[i+int(window/2)]],mag,sint,window,overlap,fft,detrend,Tmin,Tmax)
                else:
                    df=zero_crossing(df,[time[i+int(window/2)]],mag,sint)


    return df


