""" Fill NA/NaN values using the specified method.


    Parameters
    ~~~~~~~~~~

    input_array : (Panda Obj)
        The Panda dataframe.

    value, float
        Value to use to fill holes (e.g. 0),

    limit, int
        If method is specified, this is the maximum number of consecutive NaN
        values to forward/backward fill. In other words, if there is a gap
        with more than this number of consecutive NaNs, it will only be partially filled.

    method {‘backfill’, ‘bfill’, ‘pad’, ‘ffill’, None}, default None
        Method to use for filling holes in reindexed Series pad / ffill: propagate last valid
        observation forward to next valid backfill / bfill: use next valid observation to fill
        gap.
    
    Note
    ~~~~

    See https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.fillna.html

"""

def fill(input_array,args={'value':float(),'limit':int(),'method':{"backfill": False,"bfill":False,\
						"pad":False, "ffill":False,"None":True}}):


    #method=[key for key in args['method'] if args['method'][key]][0]
    method=args['method']
    if method=='None':
       method=None
    input_array=input_array.fillna(value=args['value'], method=None, limit=args['limit'])
    
    return input_array


