"""Extract a timeseries by selected a time interval

    Parameters
    ~~~~~~~~~~

    input_array : (Panda Obj)
        The Panda dataframe.
    method: {"min/max time","Annual","Monthly","Seasonal","Custom"}
        If ``method == 'min/max time'``,
            the selected timeseries will be between the ``minimum time``
            and ``maximum time``
        If ``method == 'Annual'``,
            The selected timeseries will be between split between each years
        If ``method == 'Monthly'``,
            The selected timeseries will be between split between each months
        If ``method == 'Seasonal'``,
            The selected timeseries will be between split between each seasons
        If ``method == 'Custom'``,
            The selected timeseries will be between split between each selected months
            from the list ``month(s)``.
    minimum time : datetime
        The minimum timestamp
    maximum time : datetime
        The maximum timestamp
    month(s) : list
        list of the month to extract

    Examples:
    ~~~~~~~~~

    >>> df['selected']=select_by_time.select_by_time(df['signal'].copy(),
    args={'minimum time':datetime.datetime(2020,1,1),
        'maximum time':datetime.datetime(2020,2,1),
        'month(s)':[1,2],
        'method':'Annual',
        })
    >>> 

"""
from datetime import datetime,date
from matplotlib.dates import date2num
import pandas as pd


def select_by_time(input_array,args={'minimum time':datetime,'maximum time':datetime,\
                        'month(s)':list(),'method':{"min/max time": True,"Annual":False,\
                        "Monthly":False,'Seasonal':False,'Custom':False}}):


    method=args['method']#[key for key in args['method'] if args['method'][key]][0]

    if method=='min/max time':
        mask = (date2num(input_array.index) >= date2num(args['minimum time'])) & (date2num(input_array.index) <= date2num(args['maximum time']))
        input_array=input_array.loc[mask]

    elif method=='Monthly':
        name=input_array.name
        input_array = pd.DataFrame(input_array)
        all_month=input_array.index.month
         
        for month in all_month.unique():
            month_str = date(1900, month, 1).strftime('%B')
            mask=all_month==month
            input_array[name+'_'+month_str]=input_array[name].loc[mask]

        del input_array[name]

    elif method=='Annual':
        name=input_array.name
        input_array = pd.DataFrame(input_array)
        all_year=input_array.index.year
         
        for year in all_year.unique():
            year_str = str(year)
            mask=all_year==year
            input_array[name+'_'+year_str]=input_array[name].loc[mask]

        del input_array[name]

    elif method=='Seasonal':
        name=input_array.name
        input_array = pd.DataFrame(input_array)
        all_month=input_array.index.month
        seasons=[12,1,2]
        seasons.append([3,4,5])
        seasons.append([6,7,8])
        seasons.append([9,10,11])

        for season in seasons:
            season_str = date(1900, season[0], 1).strftime('%b')+'_to_'+date(1900, season[-1], 1).strftime('%b')
            mask=(all_month>=season[0]) & (all_month<=season[-1])
            input_array[name+'_'+season_str]=input_array[name].loc[mask]

        del input_array[name]

    else:
        name=input_array.name
        input_array = pd.DataFrame(input_array)
        all_month=input_array.index.month
        if ',' in args['month(s)']:
            choosen_month=map(int, args['month(s)'].split(','))
        else:
            choosen_month=[int(x) for x in args['month(s)']]
        mask=False
        for m in choosen_month:
            mask+=m==all_month
       
        input_array[name+'_custom']=input_array[name].loc[mask]

        del input_array[name]


    return input_array