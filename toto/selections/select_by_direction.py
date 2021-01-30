"""Extract a portion of timeseries by direction

"""

from ..core.toolbox import dir_interval
import pandas as pd

def select_by_direction(input_array,args={'From':float,'To':float,'dir swath':float,'method':{"Custom":False,"centred": True,"not-centred":False}}):

	#method=[key for key in args['method'] if args['method'][key]][0]
	method=args['method']
	name=input_array.name

	if method == 'Custom':
		interval=[args['From'],args['To']]
	else:
		interval=dir_interval(dir_swath=args['dir swath'],mode=method)
	
	input_array = pd.DataFrame(input_array)
	for k in range(0,len(interval)-1):
            if k==1 and method != 'Custom':
                if method == 'centred':
                    mask=np.logical_or(input_array.index >= interval[k],input_array.index <= interval[k+1])
                else:
                    mask=(input_array.index >= interval[k]) & (input_array.index <= interval[k+1])
                
            else:
                mask=(input_array.index > interval[k]) & (input_array.index <= interval[k+1])

            new_name='%s_%.1f_%.1f' % (name,interval[k],interval[k+1])
            input_array[new_name]=input_array[name].loc[mask]
            

	del input_array[name]

	return input_array




