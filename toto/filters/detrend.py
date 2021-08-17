""" Remove linear trend along axis from data.
   
    Parameters
    ~~~~~~~~~~
    input_array : panda obj
        The input data.
    Type : {'linear', 'constant'}, optional
        The type of detrending.
        If ``type == 'linear'`` (default),
            The result of a linear least-squares fit to `data` is subtracted
            from `data`.
        If ``type == 'constant'``,
            only the mean of `data` is subtracted.

	Note
	~~~~
    see <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.detrend.html>_ for more info
"""
from scipy import signal

def detrend(input_array,args={'Type':{'linear':True, 'constant':False}}):

	#mode=[key for key in args['Type'] if args['Type'][key]][0]
	mode=args['Type']
	input_array=signal.detrend(input_array,type=mode)

	return  input_array