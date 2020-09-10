import numpy as np
import datetime
from ...core.toolbox import dir_interval,get_increment,get_number_of_loops
from ...core.make_table import create_table

def modal_tm(h,t,p=95):
    idx=(h>=np.nanpercentile(h,p)) #find top 5% of wave height      
    return np.nanmean(t[idx]) #modal period
def nrj_weighted(h,drr):
    h[np.isnan(h)]=0
    drr[np.isnan(drr)]=0
    drr=(270-drr)*(np.pi/180.)
    u=np.sum(h**2*np.sin(drr))
    v=np.sum(h**2*np.cos(drr))
    e=np.arctan2(u,v)
    return np.mod(270-(180*e)/np.pi,360)

def do_occurence(dpm,min_occ):
    dir_int=dir_interval(45,'centred')
    dir_int_name=np.array(['N','NE','E','SE','S','SW','W','NW'])
    occ=np.ones((len(dir_int)-1))
    for j in range(0,len(dir_int)-1):
        if dir_int[j+1] <= dir_int[j]:
            D=((np.mod(dpm,360)>dir_int[j]) | (np.mod(dpm,360)<=dir_int[j+1]))
        else:
            D=((np.mod(dpm,360)>dir_int[j]) & (np.mod(dpm,360)<=dir_int[j+1]))
        
        occ[j]=(len(D)/len(dpm[~np.isnan(dpm)]))*100;
    

    Occ=dir_int_name[np.where(occ>=min_occ)]
    return Occ


def do_weighted_direction(time,hs,drr,hem,filename):
    year=time.year
    month=time.month

    mat=[]
    row=['','Energy weighted direction']
    mat.append(row)
    # monthly stats
    for mo in range(1,13):   
        idx=month==mo
        if any(idx):
            row=[datetime.date(1900, mo, 1).strftime('%B')]
            row.append('%.2f'%nrj_weighted(hs[idx],drr[idx]))
            mat.append(row)

    # Do seasons
    if hem=='South hemisphere(Summer/Winter)':
        seas=[((month<=3) | (month>=10))] # Summer: October to March
        seas.append(((month>=4) & (month<=9))) # Winter: April to September
        sea_names=['Summer','Winter']

    elif hem=='South hemisphere 4 seasons':
        seas=[(month>=6) & (month <=8)]# winter
        seas=[(month>=9) & (month <=11)]# spring
        seas=[(month>=12) | (month<=2)]#summer
        seas=[(month>=3) & (month<=5)]# autumn
        sea_names=['Winter','Spring','Summer','Autumn']
    elif hem =='North hemishere(Summer/Winter)':
        seas=[(month>=4) & (month<=9)]  # Winter: April to September
        seas=[(month<=3) | (month>=10)] # Summer: October to March
        sea_names=['Summer','Winter']
    elif hem=='North hemisphere moosoon(SW,NE,Hot season)':
        seas=[(month>=5) & (month<=10)] # SW: May to Oct
        seas=[(month<=2) | (month>=11)] # SE: Nov to Feb
        seas=[(month==3) | (month==4)] # Hot: March and April
        sea_names=['SW monsoon','NE monsoon','Hot season']
    elif hem=='North hemisphere 4 seasons':
        seas=[(month>=12) | (month<=2)] # winter
        seas=[(month>=3) & (month<=5)] # spring
        seas=[(month>=6) & (month <=8)] # summer
        seas=[(month>=9) & (month <=11)] # autumn
        sea_names=['Winter','Spring','Summer','Autumn']


    for i,idx in enumerate(seas):
        if any(idx):
            row=[sea_names[i]]
            row.append('%.2f'%nrj_weighted(hs[idx],drr[idx]))
            mat.append(row)

    # %% Do total
    row=['Total']
    row.append('%.2f'%nrj_weighted(hs,drr))
    mat.append(row)
    create_table(filename,'',np.array(mat))

def do_modal_stat(time,hs,tp,hem,filename):
    year=time.year
    month=time.month

    mat=[]
    row=['','Modal Wave Period']
    mat.append(row)
    # monthly stats
    for mo in range(1,13):   
        idx=month==mo
        if any(idx):
            row=[datetime.date(1900, mo, 1).strftime('%B')]
            row.append('%.2f'%modal_tm(hs[idx],tp[idx]))
            mat.append(row)

    # Do seasons
    if hem=='South hemisphere(Summer/Winter)':
        seas=[((month<=3) | (month>=10))] # Summer: October to March
        seas.append(((month>=4) & (month<=9))) # Winter: April to September
        sea_names=['Summer','Winter']

    elif hem=='South hemisphere 4 seasons':
        seas=[(month>=6) & (month <=8)]# winter
        seas=[(month>=9) & (month <=11)]# spring
        seas=[(month>=12) | (month<=2)]#summer
        seas=[(month>=3) & (month<=5)]# autumn
        sea_names=['Winter','Spring','Summer','Autumn']
    elif hem =='North hemishere(Summer/Winter)':
        seas=[(month>=4) & (month<=9)]  # Winter: April to September
        seas=[(month<=3) | (month>=10)] # Summer: October to March
        sea_names=['Summer','Winter']
    elif hem=='North hemisphere moosoon(SW,NE,Hot season)':
        seas=[(month>=5) & (month<=10)] # SW: May to Oct
        seas=[(month<=2) | (month>=11)] # SE: Nov to Feb
        seas=[(month==3) | (month==4)] # Hot: March and April
        sea_names=['SW monsoon','NE monsoon','Hot season']
    elif hem=='North hemisphere 4 seasons':
        seas=[(month>=12) | (month<=2)] # winter
        seas=[(month>=3) & (month<=5)] # spring
        seas=[(month>=6) & (month <=8)] # summer
        seas=[(month>=9) & (month <=11)] # autumn
        sea_names=['Winter','Spring','Summer','Autumn']


    for i,idx in enumerate(seas):
        if any(idx):
            row=[sea_names[i]]
            row.append('%.2f'%modal_tm(hs[idx],tp[idx]))
            mat.append(row)

    # %% Do total
    row=['Total']
    row.append('%.2f'%modal_tm(hs,tp))
    mat.append(row)
    create_table(filename,'',np.array(mat))

def do_stats(time,statf,data,drr,hem,filename,sheetname):


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
                    if isinstance(stat,str):
                        fct=getattr(np, 'nan'+stat)
                        row.append('%.2f'%fct(data[idx]))
                    elif isinstance(stat,list):
                        perc=list(np.percentile(data[idx],stat))
                        row+=['%.2f'%x for x in perc]
                    else:
                        if not isinstance(drr,str):
                            for min_occ in [15,10,5,1]:
                                occ=do_occurence(drr[idx],min_occ)
                                if len(occ)>0:
                                    break
                            row.append(', '.join(occ))

                mat.append(row)



        # Do seasons
        if hem=='South hemisphere(Summer/Winter)':
            seas=[((month<=3) | (month>=10))] # Summer: October to March
            seas.append(((month>=4) & (month<=9))) # Winter: April to September
            sea_names=['Summer','Winter']

        elif hem=='South hemisphere 4 seasons':
            seas=[(month>=6) & (month <=8)]# winter
            seas=[(month>=9) & (month <=11)]# spring
            seas=[(month>=12) | (month<=2)]#summer
            seas=[(month>=3) & (month<=5)]# autumn
            sea_names=['Winter','Spring','Summer','Autumn']
        elif hem =='North hemishere(Summer/Winter)':
            seas=[(month>=4) & (month<=9)]  # Winter: April to September
            seas=[(month<=3) | (month>=10)] # Summer: October to March
            sea_names=['Summer','Winter']
        elif hem=='North hemisphere moosoon(SW,NE,Hot season)':
            seas=[(month>=5) & (month<=10)] # SW: May to Oct
            seas=[(month<=2) | (month>=11)] # SE: Nov to Feb
            seas=[(month==3) | (month==4)] # Hot: March and April
            sea_names=['SW monsoon','NE monsoon','Hot season']
        elif hem=='North hemisphere 4 seasons':
            seas=[(month>=12) | (month<=2)] # winter
            seas=[(month>=3) & (month<=5)] # spring
            seas=[(month>=6) & (month <=8)] # summer
            seas=[(month>=9) & (month <=11)] # autumn
            sea_names=['Winter','Spring','Summer','Autumn']


        for i,idx in enumerate(seas):
            if any(idx):
                row=[sea_names[i]]
                for stat in statf:
                    if isinstance(stat,str):
                        fct=getattr(np, 'nan'+stat)
                        row.append('%.2f'%fct(data[idx]))
                    elif isinstance(stat,list):
                        perc=list(np.percentile(data[idx],stat))
                        row+=['%.2f'%x for x in perc]
                    else:
                        if not isinstance(drr,str):
                            for min_occ in [15,10,5,1]:
                                occ=do_occurence(drr[idx],min_occ)
                                if len(occ)>0:
                                    break
                            row.append(', '.join(occ))

                mat.append(row)

        # %% Do total
        row=['Total']
        for stat in statf:
            if isinstance(stat,str):
                fct=getattr(np, 'nan'+stat)
                row.append('%.2f'%fct(data))
            elif isinstance(stat,list):
                perc=list(np.percentile(data,stat))
                row+=['%.2f'%x for x in perc]
            else:
                if not isinstance(drr,str):
                    for min_occ in [15,10,5,1]:
                        occ=do_occurence(drr,min_occ)
                        if len(occ)>0:
                            break
                    row.append(', '.join(occ))

        mat.append(row)
        create_table(filename,sheetname,np.array(mat))
