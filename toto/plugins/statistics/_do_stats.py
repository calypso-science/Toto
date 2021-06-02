import numpy as np
import datetime
from ...core.toolbox import dir_interval,get_increment,get_number_of_loops,do_occurence
from ...core.make_table import create_table
from ...core.toolbox import display_message

def do_stats(time,statf,data,drr,hem,filename,sheetname,min_occ):

        year=time.year
        month=time.month

        mat=[]
        row=['']
        for stat in statf:
            if isinstance(stat,str):
                row.append(stat)
            elif isinstance(stat,list):
                for p in stat:
                    row.append('P'+str(p))
            else:
                row.append('Main direction')

        mat.append(row)



        # monthly stats
        for mo in range(1,13):   
            idx=month==mo
            if any(idx):
                row=[datetime.date(1900, mo, 1).strftime('%B')]
                for stat in statf:
                    if stat=='n':
                        tmp=data[idx]
                        row.append('%.2f'%len(tmp[~np.isnan(tmp)]))
                    elif isinstance(stat,str):
                        fct=getattr(np, 'nan'+stat)
                        row.append('%.2f'%fct(data[idx]))
                    elif isinstance(stat,list):
                        perc=list(np.nanpercentile(data[idx],stat))
                        row+=['%.2f'%x for x in perc]
                    else:
                        if not isinstance(drr,str):
                            #for min_occ in [15,10,5,1]:
                            occ=do_occurence(drr[idx].values,min_occ)
                            #    if len(occ)>0:
                            #        break
                            row.append(', '.join(occ))

                mat.append(row)



        # Do seasons
        if hem=='South hemisphere(Summer/Winter)':
            seas=[((month<=3) | (month>=10))] # Summer: October to March
            seas.append(((month>=4) & (month<=9))) # Winter: April to September
            sea_names=['Summer','Winter']

        elif hem=='South hemisphere 4 seasons':
            seas=[(month>=6) & (month <=8)]# winter
            seas.append((month>=9) & (month <=11))# spring
            seas.append((month>=12) | (month<=2))#summer
            seas.append((month>=3) & (month<=5))# autumn
            sea_names=['Winter','Spring','Summer','Autumn']
        elif hem =='North hemishere(Summer/Winter)':
            seas=[(month>=4) & (month<=9)]  # Winter: April to September
            seas.append((month<=3) | (month>=10)) # Summer: October to March
            sea_names=['Summer','Winter']
        elif hem=='North hemisphere moosoon(SW,NE,Hot season)':
            seas=[(month>=5) & (month<=10)] # SW: May to Oct
            seas.append((month<=2) | (month>=11)) # SE: Nov to Feb
            seas.append((month==3) | (month==4)) # Hot: March and April
            sea_names=['SW monsoon','NE monsoon','Hot season']
        elif hem=='North hemisphere 4 seasons':
            seas=[(month>=12) | (month<=2)] # winter
            seas.append((month>=3) & (month<=5)) # spring
            seas.append((month>=6) & (month <=8)) # summer
            seas.append((month>=9) & (month <=11)) # autumn
            sea_names=['Winter','Spring','Summer','Autumn']
        elif hem == 'Yearly':
            unique_year=np.unique(year)
            seas=[]
            sea_names=[]
            for y in unique_year:
                seas.append(year==y)
                sea_names.append('%i' % y)


        for i,idx in enumerate(seas):
            if any(idx):
                row=[sea_names[i]]
                for stat in statf:
                    if stat=='n':
                        tmp=data[idx]
                        row.append('%.2f'%len(tmp[~np.isnan(tmp)]))
                    elif isinstance(stat,str):
                        fct=getattr(np, 'nan'+stat)
                        row.append('%.2f'%fct(data[idx]))
                    elif isinstance(stat,list):
                        perc=list(np.nanpercentile(data[idx],stat))
                        row+=['%.2f'%x for x in perc]
                    else:
                        if not isinstance(drr,str):
                            #for min_occ in [15,10,5,1]:
                            occ=do_occurence(drr[idx].values,min_occ)
                            #    if len(occ)>0:
                            #        break
                            row.append(', '.join(occ))

                mat.append(row)

        # %% Do total
        row=['Total']
        for stat in statf:
            if stat=='n':
                row.append('%.2f'%len(data[~np.isnan(data)]))
            elif isinstance(stat,str):
                fct=getattr(np, 'nan'+stat)
                row.append('%.2f'%fct(data))
            elif isinstance(stat,list):
                perc=list(np.nanpercentile(data,stat))
                row+=['%.2f'%x for x in perc]
            else:
                if not isinstance(drr,str):
                    #for min_occ in [15,10,5,1]:
                    occ=do_occurence(drr.values,min_occ)
                    #    if len(occ)>0:
                    #        break
                    row.append(', '.join(occ))

        mat.append(row)
        create_table(filename,sheetname,np.array(mat))
