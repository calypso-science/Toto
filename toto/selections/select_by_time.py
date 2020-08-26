"""Extract a portion of as timeseries

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