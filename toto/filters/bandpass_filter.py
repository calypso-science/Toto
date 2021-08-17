"""Creates  Fourier low, high, or bandpass filter.

    Parameters
    ~~~~~~~~~~

    input_array : (Panda Obj)
        The Panda dataframe.
    lower cut-off (s) : float
        The minimum period filter cutoff
    upper cut-off (s) : float
        The maximum period filter cutoff


    Notes
    ~~~~~
    
        * lower cut-off set < (2*delt) for no cutoff at high freq end
        * upper cut-off set > (length(data)*delt) for no cutoff at low freq end

    Examples:
    ~~~~~~~~~

    >>> df['bandpass']=bandpass_filter.bandpass_filter(df['signal'].copy(),\
    args={'lower cut-off (s)':3600*30,'upper cut-off (s)':24*3600*30})
    >>> 


"""




import numpy as np
from scipy.fftpack import fft,ifft,rfft, irfft, fftfreq
from toto.core.toolbox import dyadlength

def bandpass_filter(input_array,args={'lower cut-off (s)':float(),'upper cut-off (s)':float()}):

    
    output_array=input_array.copy()
    delt=(input_array.index[1]-input_array.index[0]).total_seconds()/3600 # in hours
    tmin=args['lower cut-off (s)']
    tmax=args['upper cut-off (s)']

    if tmin == None or tmin ==0:
        tmin=delt*2.
    else:
        tmin=tmin/3600.

    if tmax == None or tmax ==0:
        tmax=len(output_array.values)*delt
    else:
        tmax=tmax/3600.

    nan_ind=np.isnan(input_array)
    
    input_array.interpolate(inplace=True) #linear interp between gaps


    trend=np.nanmean(input_array)
    input_array=input_array-trend #% remove trend
    input_array[np.isnan(input_array)]=0 #remove NaN which are on edges of time series and not filled by interp1

    npts_orig,J=dyadlength(input_array.values)

    npts=2**J #;%least power of two greater than npts_orig
    if npts-npts_orig<npts/16:
        npts=2**(J+1) #;%2nd least power of two greater than npts_orig if not enough zeros

    nby2=(npts/2)
    data_padded=np.zeros((int(npts),))

    data=input_array.values
    
    #adjust the padding with first and last value of the time series 
    data_padded[:int(np.round(npts/2))]=data[(~np.isnan(data)).nonzero()[0][0]]
    data_padded[int(np.round(npts/2)):]=data[(~np.isnan(data)).nonzero()[0][-1]]
    data_padded[int(nby2-np.round(npts_orig/2)):int(nby2-np.round(npts_orig/2)+npts_orig)]=data
    data=data_padded #clear data_padded

    #readjust to have zero mean
    data=data-np.nanmean(data)

    tfund=npts*delt
    ffund=1.0/tfund

    # fourier transform data:
    coeffs = fft(data)

    #  filter coefficients:
    f=np.cumsum(ffund*np.ones((int(nby2),)))
    t=np.concatenate(([np.NaN],1.0/f))
    idx=np.logical_or(t > tmax , t < tmin)
    coeffs[idx.nonzero()[0]]=0.0

    #  calculate the remaining coefficients:
    
    coeffs[int(npts+1-nby2):int(npts)]=np.conj(coeffs[int(nby2-1):0:-1])

    #  backtransform data and take real part:

    backcoeffs=ifft(coeffs)
    filtdat=np.real(backcoeffs)

    filtdat=filtdat[int(nby2-round(npts_orig/2)):int(nby2-round(npts_orig/2)+npts_orig)] #;%remove padded zeros
    filtdat=filtdat+trend #;% add back the trend
    filtdat[nan_ind]=np.NaN;


    output_array.values[:]=filtdat

    return output_array