"""	Replace NaN values
	Methods:
		- Backfill
		- bfill
		- pad
		- ffill
	See: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.fillna.html
	
"""

def fill(input_array,args={'value':float(),'limit':int(),'method':{"backfill": False,"bfill":False,\
						"pad":False, "ffill":False,"None":True}}):


    #method=[key for key in args['method'] if args['method'][key]][0]
    method=args['method']
    if method=='None':
       method=None
    input_array=input_array.fillna(value=args['value'], method=None, limit=args['limit'])
    
    return input_array


