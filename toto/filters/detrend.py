"""Detrending a signal
Methods:
 - Linear (default)
 - Constant
see https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.detrend.html for more info
"""
from scipy import signal

def detrend(input_array,args={'Type':{'linear':True, 'constant':False}}):

	#mode=[key for key in args['Type'] if args['Type'][key]][0]
	mode=args['Type']
	input_array=signal.detrend(input_array,type=mode)

	return  input_array