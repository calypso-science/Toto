
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

    T=1./freqs;

    if plotfreq:
        xlab='Frequency'
        xlab_unit='Hz'
        X=freqs
    else:
        xlab='Period'
        xlab_unit='s'
        X=T

    if max(T)>2*3600 and not plotfreq:
        T=T/3600.
        freqs=freqs*3600.
        Tmin=Tmin/3600.
        Tmax=Tmax/3600.
        xlab_unit='h'

    fig = plt.figure(figsize=(8.27, 11.69), dpi=100)
    ax =fig.add_subplot(111)
    if ~plotfreq and Tmax>200:
        plt.loglog(X,psd)
    else:
        plt.semilogy(X,psd)


    ax.grid(True)
    ax.set_xlabel(xlab+' ['+xlab_unit+']')
    ax.set_ylabel('PSD [('+unit+')^2 .times s]')
  

    if plotfreq:
        ax.set_xlim(1/Tmax,1/Tmin)
    else:
        ax.set_xlim(Tmin,1/Tmax)


    plt.savefig(fileout)
    plt.show(block=~display)