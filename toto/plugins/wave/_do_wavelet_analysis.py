
import numpy as np
from ...filters.bandpass_filter import bandpass_filter
from ...core.waveletFunctions import wavelet, wave_signif
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
import matplotlib.ticker as ticker
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import pyplot as plt

def do_wavelet(time,mag,mother,period,dj,unit,filename,display):

    dj=1/dj
    dt=(time[2]-time[1]).total_seconds()
    Tmin=period[0]
    Tmax=period[1]

    lag1 = 0.72  # lag-1 autocorrelation for red noise background
    if mother=='Morlet':
        fac=1.033
    elif mother=='Paul':
        fac=1.3963
    elif mother=='DOG':
        fac=3.9738
    else:
        assert 'method not understood'

    min_power_of2_filt=np.floor(np.log2(Tmin/dt))
    max_power_of2_filt=np.ceil(np.log2(Tmax/dt))

    min_power_of2=np.floor(np.log2(Tmin/fac/dt))
    max_power_of2=np.ceil(np.log2(Tmax/fac/dt))

    s0 = 2**(min_power_of2)*dt
    j1 = (max_power_of2-min_power_of2)/dj;    # this says do (max_power_of2-min_power_of2) powers-of-two above min_power_of2 with dj sub-octaves each

    mag=bandpass_filter(mag,args={'lower cut-off (s)':2**(min_power_of2_filt)*dt,'upper cut-off (s)':2**(max_power_of2_filt)*dt})

    mag=mag.values
    n = len(mag);
    variance = np.nanstd(mag, ddof=1)**2;


    if len(mag)*j1>30000000:
      assert 'Number of data too large to perform wavelet analysis, please:\n'+\
          '- reduce the time window, or\n- reduce the sub-octave number, or\n- reduce the period window'


    # Wavelet transform:
    wave,period,scale,coi = wavelet(mag,dt,1,dj,s0,j1,mother.upper())
    coi=coi[:-1]

    power = (np.abs(wave))**2         # compute wavelet power spectrum

    # Global wavelet spectrum 
    global_ws = variance*(np.sum(power,axis=1)/n)#   % time-average over all times

    # Scale-average between Tmin and Tmax
    avg = np.logical_and(period >= Tmin,period < Tmax)
    Cdelta = 0.776 #   % this is for the MORLET wavelet
    scale_avg = scale[:, np.newaxis].dot(np.ones(n)[np.newaxis, :])  # expand scale --> (J+1)x(N) array
    scale_avg = power / scale_avg #   % [Eqn(24)]
    scale_avg = variance*dj*dt/Cdelta*sum(scale_avg[avg,:]) #   % [Eqn(24)]
    scaleavg_signif = wave_signif(variance, dt=dt, scale=scale, sigtest=2,
        lag1=lag1, dof=([2, 7.9]), mother=mother.upper())
    # Significance levels:
    signif = wave_signif(([variance]), dt=dt, sigtest=0, scale=scale,
        lag1=lag1, mother=mother.upper())
    sig95 = signif[:, np.newaxis].dot(np.ones(n)[np.newaxis, :])  # expand signif --> (J+1)x(N) array
    sig95 = power / sig95  # where ratio > 1, power is significant


    # Global wavelet spectrum & significance levels:
    dof = n - scale  # the -scale corrects for padding at edges
    global_signif = wave_signif(variance, dt=dt, scale=scale, sigtest=1,
        lag1=lag1, dof=dof, mother=mother.upper())

# fig=figure;

# %------------------------------------------------------ Plotting

    Tmin_plot=2**(min_power_of2_filt)*dt;
    Tmax_plot=2**(max_power_of2_filt)*dt;

    #find the appropriate period unit
    if Tmax_plot>3600*24*2:
        period = period/(3600*24)
        Tmin=Tmin/(3600*24)
        Tmax=Tmax/(3600*24)
        Tmin_plot=Tmin_plot/(3600*24)
        Tmax_plot=Tmax_plot/(3600*24)
        t_unit='days'
    elif Tmax_plot>3600*6:
        period = period/3600
        Tmin=Tmin/3600;Tmax=Tmax/3600
        Tmin_plot=Tmin_plot/3600
        Tmax_plot=Tmax_plot/3600
        t_unit='h'
    else:
        t_unit='s'
    

    #--- Plot time series
    fig = plt.figure(figsize=(8.27, 11.69), dpi=100)
    gs = GridSpec(3, 4, hspace=0.4, wspace=0.75)
    plt.subplots_adjust(left=0.1, bottom=0.05, right=0.9, top=0.95, wspace=0, hspace=0)
    plt.subplot(gs[0, 0:3])
    plt.plot(time, mag, 'k')
    plt.xlim([min(time),max(time)])
    plt.xlabel('Time (year)')
    plt.ylabel('Elevation ['+unit+']')
    plt.title('Sea Surface elevation')
    fig.autofmt_xdate()



    # #increase the time interval if the contour is too dense
    # if len(time)>10000
    #     while len(time)>20000:
    #         time=time(1:2:end);
    #         scale_avg=mov_avg(scale_avg,2);
    #         for i=1:size(power,1)
    #        power(i,:)=mov_avg(power(i,:),2);
    #         end
    #         scale_avg=scale_avg(1:2:end);
    #         power=power(:,1:2:end);
    #         coi=coi(1:2:end);
    #     end
    # end


    plt3 = plt.subplot(gs[1, 0:3])
    levels = np.linspace(np.min(power),np.max(power),5)

    CS = plt.contourf(time, period, power, len(levels))  #*** or use 'contour'
    im = plt.contourf(CS, levels=levels, colors=['white','bisque','orange','orangered','darkred'])
    plt.ylabel('Period (years)')
    plt.title('Wavelet Power Spectrum')
    plt.xlim([min(time),max(time)])
    # 95# significance contour, levels at -99 (fake) and 1 (95# signif)
    #plt.contour(time, period, sig95, [-99, 1], colors='k')
    # cone-of-influence, anything "below" is dubious
    plt.plot(time, coi, 'k')
    # format y-scale
    #plt.show()
    plt3.set_yscale('log', basey=2, subsy=None)
    plt.ylim([np.min(period), np.max(period)])
    ax = plt.gca().yaxis
    ax.set_major_formatter(ticker.ScalarFormatter())
    plt3.ticklabel_format(axis='y', style='plain')
    plt3.invert_yaxis()

    plt.colorbar()


    #--- Plot global wavelet spectrum
    plt4 = plt.subplot(gs[1, -1])
    plt.plot(global_ws, period)
    #plt.plot(global_signif, period, '--')
    plt.xlabel('Power ('+unit+'$^2$)')
    #plt.show()
    plt.title('Global Wavelet Spectrum')
    plt.xlim([0, 1.25 * np.max(global_ws)])
    # format y-scale
    plt4.set_yscale('log', basey=2, subsy=None)
    plt.ylim([np.min(period), np.max(period)])
    ax = plt.gca().yaxis
    ax.set_major_formatter(ticker.ScalarFormatter())
    plt4.ticklabel_format(axis='y', style='plain')
    plt4.invert_yaxis()

    # --- Plot 2--8 yr scale-average time series
    plt.subplot(gs[2, 0:3])
    plt.plot(time, scale_avg, 'k')
    plt.xlim([min(time),max(time)])
    plt.ylabel('Avg variance ('+unit+'$^2$)')
    plt.title('Scale-average Time Series')
    xlim=[min(time),max(time)]
    #plt.plot(xlim, scaleavg_signif + [0, 0], '--')
    
    #fig.autofmt_xdate()
    plt.subplots_adjust(bottom=0.02)


    if display:
        plt.show(block=~display)
    plt.savefig(filename)
