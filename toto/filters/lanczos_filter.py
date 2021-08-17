""" Apply a low pass 1st or 2nd order lanczos filter
   
    Parameters
    ~~~~~~~~~~

    input_array : panda obj
        The input data.
    window : int
        window in hour, a good window is 40 h window of hourly data
    Type : {'lanczos lowpas 1st order', 'lanczos lowpas 2nd order'}, optional
        The type of lowpass filter, first or second order

"""

from scipy.signal import butter, filtfilt, detrend
from oceans.filters import lanc
import numpy as np



def lanczos_filter(input_array,args={'window':int(),\
                                    'Type':{'lanczos lowpas 1st order':True,
                                            'lanczos lowpas 2nd order':False}
                                    }):

    window=args['window']
    filter_type=args['Type']
    mean = input_array.mean()
    delt=(input_array.index[1]-input_array.index[0]).total_seconds()/3600 # in hours
    
    if filter_type == 'lanczos lowpas 1st order':
        input_array= lanczos_lowpass_first_order(input_array - mean, window, dt=delt, order=3) + mean
    elif filter_type == 'lanczos lowpas 2nd order':
        input_array= lanczos_lowpass_second_order(input_array - mean, window, dt=delt, order=3) + mean

    return input_array


def lanczos_lowpass_second_order(data, window, dt=1, order=5):
    
    
    """
    Inpulse response filter
    """

    fs   = (2*np.pi) / (dt*3600)
    nyq  = 0.5 * fs
    C    = 0.802

    window  = int( window / dt )
    highcut = (2*np.pi) / (window*3600)

    high = (highcut / nyq) #/ C # to prevent phase lag
    
    
    m = window*5 # Rule of thumb is 120 point for a 40 h window of hourly data
    
    coefs=lanczos_lowpass_filter_coeffs(high, m)#window)
    
    d2 = filtfilt(coefs,[1.0],data,axis=0)#,padtype=padtype,padlen=padlen)
    
    #d2 = np.convolve(data, coefs, 'same')
    
    #if(len(idx)>0):
    #    d2[result_nan_idx]=nan
    
    ## replace edge points with nan if pading is not used
    #if (padtype is None) and (fill_edge_nan==True):
    d2[0:2*m]=np.nan
    d2[len(d2)-2*m:len(d2)]=np.nan

    return d2

def lanczos_lowpass_first_order(data, window, dt=1, order=5):
    
    freq = 1./window  # Hours
    
    window = int( window / dt )
    pad = np.zeros(window) * np.NaN

    wt = lanc(window, freq)
    wt = lanc(5*window, freq)

    return np.convolve(wt, data, mode='same')

def lanczos_lowpass_filter_coeffs(cf,m,normalize=True):
    """return the convolution coefficients for low pass lanczos filter.
      
    Parameters
    ~~~~~~~~~~
    
    Cf: float
      Cutoff frequency expressed as a ratio of a Nyquist frequency.
                  
    M: int
      Size of filtering window size.
        
    Returns
    ~~~~~~~
    Results: list
           Coefficients of filtering window.
    
    """
    
    coscoef=[cf*np.sin(np.pi*k*cf)/(np.pi*k*cf) for k in range(1,m+1,1)]
    sigma=[np.sin(np.pi*k/m)/(np.pi*k/m) for k in range(1,m+1,1)]
    prod= [c*s for c,s in zip(coscoef,sigma)]
    temp = prod[-1::-1]+[cf]+prod
    res=np.array(temp)
    if normalize:
        res = res/res.sum()
    return res