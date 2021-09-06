
from scipy import signal
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

def do_wave_spectra_plot(time,mag,unit,nperseg,noverlap,nfft,detrend,period,plotfreq,fileout,display):

    sint=(time[2]-time[1]).total_seconds()
    Tmin=period[0]
    Tmax=period[1]
    if period[0] <= 1.9999*sint:
        return print('The minimum analysed period must be at least twice the sampling period (i.e. >= '+str(2*sint)+' s)')


    if period[1] > nfft*sint:
        return print('The minimum window and nfft length must be larger than the maximum plotting period (i.e. window >= '+str(np.round(Tmax/sint))+' and nfft > '+str(np.round(Tmax/sint))+')')

    bad=np.isnan(mag)
    mag=mag[~bad] #removes possible NaN on the edges of the time series

    freqs, psd = signal.welch(mag,fs=1./sint,nperseg=int(nperseg/sint),noverlap=int(noverlap/sint),nfft=int(nfft/sint),detrend=detrend)
    psd=psd[freqs>0]
    freqs=freqs[freqs>0]
    T=1./freqs;
    xlab_unit='s'
    if max(T[np.isfinite(T)])>2*3600 and not plotfreq:
        T=T/3600.
        freqs=freqs*3600.
        Tmin=Tmin/3600.
        Tmax=Tmax/3600.
        xlab_unit='h'


    if plotfreq:
        xlab='Frequency'
        xlab_unit='Hz'
        X=freqs
    else:
        xlab='Period'
        X=T



    fig = plt.figure(figsize=(8.27, 11.69), dpi=100)
    ax =fig.add_subplot(111)
    if not plotfreq and Tmax>200:
        plt.loglog(X,psd)
    else:
        plt.semilogy(X,psd)


    ax.grid(True)
    ax.set_xlabel(xlab+' ['+xlab_unit+']')
    ax.set_ylabel('PSD [('+unit+')^2 .times s]')
  
    if plotfreq:
        ax.set_xlim(1/Tmax,1/Tmin)
        y=psd[np.logical_and(X>1/Tmax,X<1/Tmin)]
        ax.set_ylim(y.max(),y.min())        
    else:
        ax.set_xlim(Tmin,Tmax)
        y=psd[np.logical_and(X>Tmin,X<Tmax)]
        ax.set_ylim(y.min(),y.max())

    plt.savefig(fileout)
    if display:
        plt.show()

    
