
import pandas as pd
import os
import numpy as np
from ...core.make_table import create_table
from ...core.wavestats import calc_slp
import copy
def sub_table(stats,rp):
    
    mag= list(stats.keys())
    if 'slp' in mag:
        stats.pop('slp')
        mag= list(stats.keys())

    rvs=len(rp)
    mat=np.empty((len(mag)+1,len(rp)+1),dtype = "object")
    mat[0,0]=''
    for i,dd in enumerate(mag):
        mat[i+1,0]=dd
        mat[i+1,1:]=np.round(stats[dd]['magex'],2).astype(str)


    mat[0,1:]=np.round(rp).astype(str)
    
    return mat

def export_as_xls(df,rp,folder):
    for drr in df.peaks_index['Annual']:
        mat=sub_table(df.eva_stats['Annual'][drr],rp)
        create_table(os.path.join(folder,'EVA_'+drr+'.xlsx'),'wave',mat)

def do_extrem_stats(wind_speed10,wind_drr,
        hs,tp,tm02,dpm,
        surface_current,surface_drr,
        midwater_current,midwater_drr,
        bottom_current,bottom_drr,
        drr_interval,rv,display,h,folderout):





    ### Do wind
    wind_speed10.rename('spd',inplace=True)
    dt_name=['u60','u10','u1','u3s']
    dt=[60,10,1,3/60.]
    wind_dataframe={}

    for i,wind in enumerate(dt_name):
        wind_dataframe[i]=wind_speed10.to_frame()
        wind_dataframe[i]['drr']=wind_drr
        wind_dataframe[i][wind]=wind_dataframe[i].DataTransformation.wind_profile(ws='spd',args={
            'Level of input wind speed (in meters)':10.,\
            'Averaging period of input wind speed (in minutes)':10.,\
            'Output level (in meters)':10.,\
            'Output time averaging (in minutes)':dt[i]})
        sort_data=np.sort(np.abs(wind_dataframe[i][wind].values))
        pks_opt={}
        pks_opt['height']=sort_data[int(np.round(len(sort_data)*(95/100)))]
        pks_opt['distance']=24*(wind_dataframe[i].Extreme.sint/3600)
        wind_dataframe[i].Extreme._get_peaks(wind,drr='drr',directional_interval=drr_interval,peaks_options=pks_opt)
        wind_dataframe[i].Extreme._clean_peak()
        wind_dataframe[i].Extreme._do_EVA(wind,'','',rv,'weibull','','ml',h,False)
        if i==1:
            wind_dataframe[i].Extreme.eva_stats['Annual']['Omni'][wind]=wind_dataframe[i].Extreme.eva_stats['Annual']['Omni']
            wind_dataframe[i].Extreme._plot_cdfs(wind,display=display,folder=folderout)


    for drr in wind_dataframe[0].Extreme.peaks_index['Annual']:
        BIG=np.empty((len(dt_name)+1,len(rv)+1),dtype = "object") 
        BIG[0,1:]=rv
        for i,wind in enumerate(dt_name):
            BIG[1+i,0]=wind
            BIG[1+i,1:]=np.round(wind_dataframe[i].Extreme.eva_stats['Annual'][drr]['magex'],2).astype(str)

        create_table(os.path.join(folderout,'EVA_'+drr+'.xlsx'),'wind',np.array(BIG))

    del wind_dataframe
    ## Do the Wave

    hs.rename('hs',inplace=True)
    wave_dataframe=hs.to_frame()
    wave_dataframe['tp']=tp
    wave_dataframe['dpm']=dpm
    wave_dataframe['tm02']=tm02
    sort_data=np.sort(np.abs(wave_dataframe['hs'].values))
    pks_opt={}
    pks_opt['height']=sort_data[int(np.round(len(sort_data)*(95/100)))]
    pks_opt['distance']=24*(wave_dataframe.Extreme.sint/3600)
    wave_dataframe.Extreme._get_peaks('hs',drr='dpm',directional_interval=drr_interval,peaks_options=pks_opt)

    if 'Omni' not in wave_dataframe.Extreme.peaks_index['Annual']:
        return 'No Peak found !!'
    else:
        wave_dataframe.Extreme._clean_peak()

    if 'tp' in wave_dataframe.Extreme.data:
        wave_dataframe.Extreme.dfout['slp']=calc_slp(wave_dataframe.Extreme.data['hs'],wave_dataframe.Extreme.data['tp'],h=h)
        wave_dataframe.Extreme.dfout['slp'].mask(wave_dataframe.Extreme.dfout['slp']<0.005, inplace=True)

    wave_dataframe.Extreme._do_EVA('hs','tp','tm02',rv,'gumbel','weibull','ml',h,True)
    wave_dataframe.Extreme._plot_cdfs('hs',display=display,folder=folderout)
    wave_dataframe.Extreme._plot_contours('hs',rv,drr='Omni',display=display,folder=folderout)
    export_as_xls(wave_dataframe.Extreme,rv,folderout)
    del wave_dataframe
    
    ### do the curent   
    current_dataframe={}

    current_dataframe[0]=surface_current.rename('surface').to_frame()
    current_dataframe[0]['drr']=surface_drr

    current_dataframe[1]=midwater_current.rename('mid-water').to_frame()
    current_dataframe[1]['drr']=midwater_drr

    current_dataframe[2]=bottom_current.rename('bottom').to_frame()
    current_dataframe[2]['drr']=bottom_drr

    names=['surface','mid-water','bottom']
    for i in range(0,3):

        sort_data=np.sort(np.abs(current_dataframe[i][names[i]].values))
        pks_opt={}
        pks_opt['height']=sort_data[int(np.round(len(sort_data)*(95/100)))]
        pks_opt['distance']=24*(current_dataframe[i].Extreme.sint/3600)
        current_dataframe[i].Extreme._get_peaks(names[i],drr='drr',directional_interval=drr_interval,peaks_options=pks_opt)
        current_dataframe[i].Extreme._clean_peak()
        current_dataframe[i].Extreme._do_EVA(names[i],'','',rv,'weibull','','ml',h,False)
        if i==0:
            current_dataframe[i].Extreme.eva_stats['Annual']['Omni'][names[i]]=current_dataframe[i].Extreme.eva_stats['Annual']['Omni']
            current_dataframe[i].Extreme._plot_cdfs(names[i],display=display,folder=folderout)


    for drr in current_dataframe[0].Extreme.peaks_index['Annual']:
        BIG=np.empty((len(names)+1,len(rv)+1),dtype = "object") 
        BIG[0,1:]=rv
        for i,wind in enumerate(names):
            BIG[1+i,0]=wind
            BIG[1+i,1:]=np.round(current_dataframe[i].Extreme.eva_stats['Annual'][drr]['magex'],2).astype(str)

        create_table(os.path.join(folderout,'EVA_'+drr+'.xlsx'),'current',np.array(BIG))



