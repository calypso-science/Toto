import numpy as np


def moving_average(input_array,args={'N-Points filter':int(),\
                                    'Mode':{"valid": False, "same":True}}):


    N=args['N-Points filter']
    #mode=[key for key in args['Mode'] if args['Mode'][key]][0]
    mode=args['Mode']

    if mode=='valid':
        y=input_array.to_numpy(copy=True)
        y_padded = np.pad(y, (N//2, N-1-N//2), mode='edge')
        input_array.values[:] = np.convolve(y_padded, np.ones((N,))/N, mode='valid') 
    else:
        input_array.values[:]=np.convolve(input_array.to_numpy(copy=True), np.ones((N,))/N, mode=mode)
    
    return input_array