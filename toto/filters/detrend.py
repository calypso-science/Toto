from scipy import signal

def detrend(input_array,args={'Type':{'linear':True, 'constant':False}}):

	mode=[key for key in args['Type'] if args['Type'][key]][0]
	input_array=signal.detrend(input_array,type=mode)

	return  input_array