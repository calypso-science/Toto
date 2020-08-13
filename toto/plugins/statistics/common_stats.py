import pandas as pd
import numpy as np
import datetime
from ...core.make_table import create_table
from ...core.toolbox import dir_interval,get_increment,get_number_of_loops
import os


@pd.api.extensions.register_dataframe_accessor("Statistics")
class Statistics:
    def __init__(self, pandas_obj):
#        self._validate(pandas_obj)
        self.data = pandas_obj
        self.dfout = pd.DataFrame(index=self.data.index.copy())


    def common_stats(self,mag='mag',drr='drr',args={'folder out':'/tmp/',
                                                    'type':{'South hemisphere(Summer/Winter)':True,\
                                                            'South hemisphere 4 seasons': False,
                                                            'North hemishere(Summer/Winter)':False,
                                                            'North hemisphere moosoon(SW,NE,Hot season)':False,
                                                            'North hemisphere 4 seasons': False
                                                            }}):

        def do_occurence(dpm,min_occ):
            dir_int=dir_interval(45,'centred')
            dir_int_name=np.array(['N','NE','E','SE','S','SW','W','NW'])
            occ=np.ones((len(dir_int)-1))
            for j in range(0,len(dir_int)-1):
                if dir_int[j+1] <= dir_int[j]:
                    D=(np.mod(dpm,360)>dir_int[j]) | (np.mod(dpm,360)<=dir_int[j+1])
                else:
                    D=(np.mod(dpm,360)>dir_int[j]) & (np.mod(dpm,360)<=dir_int[j+1])
                
                occ[j]=(len(D)/len(dpm[~np.isnan(dpm)]))*100;
            

            Occ=dir_int_name[np.where(occ>=min_occ)]
            return Occ

        if drr not in self.data:
            drr='none'

        if drr !='none':
            statf=['min','max','mean','std',[1,5,10,50,80,90,95,98,99],np.nan]
        else:
            statf=['min','max','mean','std',[1,5,10,50,80,90,95,98,99]]


        hem=args['type']


        filename='stat.xlsx'


        sheetname='caca';
        data=self.data[mag];

        time=self.data.index
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
                        if drr!='none':
                            for min_occ in [15,10,5,1]:
                                occ=do_occurence(self.data[drr][idx],min_occ)
                                if len(occ)>0:
                                    break
                            row.append(', '.join(occ))

                mat.append(row)



        # Do seasons
        hem='South hemisphere(Summer/Winter)'
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
                        if drr!='none':
                            for min_occ in [15,10,5,1]:
                                occ=do_occurence(self.data[drr][idx],min_occ)
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
                if drr!='none':
                    for min_occ in [15,10,5,1]:
                        occ=do_occurence(self.data[drr],min_occ)
                        if len(occ)>0:
                            break
                    row.append(', '.join(occ))

        mat.append(row)
        create_table(filename,sheetname,np.array(mat))


    def joint_prob(self,speed='speed',direction='direction',period='period',\
        args={'method':{'Mag vs Dir':True,'Per Vs Dir':False,'Mag vs Per':False},\
        'folder out':'/tmp/',
        'X Min Res Max(optional)':[2,1,22],
        'Y Min Res Max(optional)':[0,0.5],
        'Direction binning':{'centered':True,'not-centered':False},
        'Direction interval': 45.,
        'Time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
        'Probablity expressed in':{'percent':False,'per thoushand':True}
        }):
        ''' This function provides joint distribution tables for X and Y, i.e. the
            probability of events defined in terms of both X and Y (per 1000)
            It can be applied for magnitude-direction, magnitude-period or
            period-direction'''


        analysis_method=args['method']

        if analysis_method=='Mag vs Dir':
            Ydata=self.data[speed]
            Xdata=self.data[direction]

        elif analysis_method=='Per Vs Dir':
            Ydata=self.data[period]
            Xdata=self.data[direction]
        elif analysis_method=='Mag vs Per':
            Ydata=self.data[magnitude]
            Xdata=self.data[period]


        output_name=os.path.join(args['folder out'],'JP.xlsx')

        if args['Probablity expressed in']=='percent':
            multiplier=100.
        else:
            multiplier=1000.


        year=self.data.index.year
        month=self.data.index.month

        gd_data=~np.isnan(Xdata) & ~np.isnan(Ydata)

        Xdata=Xdata[gd_data]
        Ydata=Ydata[gd_data]
        year=year[gd_data]
        month=month[gd_data]


        Y_interval=get_increment(Ydata,args['Y Min Res Max(optional)'])
        

        if analysis_method=='Mag vs Dir' or analysis_method=='Per Vs Dir':
            X_interval=dir_interval(args['Direction interval'],args['Direction binning'])
        else:
            X_interval=get_increment(Xdata,ags['X Min Res Max(optional)'])
        

        X_interval=np.append(X_interval,np.nan)
        Y_interval=np.append(Y_interval,np.nan)


        #----------------------------------------
      
        number_of_loops,identifiers,month_identifier=get_number_of_loops(args['Time blocking'])

        for j in range(0,number_of_loops):
            #Pull out relevant indices for particular month/months
            index = np.in1d(month, month_identifier[j])
            occurrence=np.empty((len(Y_interval)-1,len(X_interval)-1))
            #Calculate Joint Probability
            big_length=len(index.nonzero()[0]);
            if big_length>0:
                for k in range(0,len(X_interval)-1):
                    if k==0:
                        if args['Direction binning']=='centred':
                            index1=(Xdata[index].values >= X_interval[k]) | (Xdata[index].values <= X_interval[k+1])
                        else:
                            index1=(Xdata[index].values >= X_interval[k]) & (Xdata[index].values <= X_interval[k+1])
                
                    elif k >0:
                        index1=(Xdata[index].values > X_interval[k]) & (Xdata[index].values <= X_interval[k+1])
            
                    for m in range(0,len(Y_interval)-1):
                        if m==1:
                            index2=index1 & (Ydata[index].values>=Y_interval[m]) & (Ydata[index].values<=Y_interval[m+1])
                        else:
                            index2=index1 & (Ydata[index].values>Y_interval[m]) & (Ydata[index].values<=Y_interval[m+1])

                        little_length=len(index2.nonzero()[0])
                        occurrence[m,k]=little_length/big_length

                occurrence=occurrence*multiplier

                occurrence[-1,:]=np.sum(np.round(occurrence,int(-np.log10(multiplier)+4)),0)
                occurrence[:,-1]=np.sum(np.round(occurrence,int(-np.log10(multiplier)+4)),1)
                occurrence[-1,-1]=multiplier

                mat=np.empty((occurrence.shape[0]+1,occurrence.shape[1]+1),dtype = "object")
                mat[0,0]=identifiers[j]
                for x in range(0,len(X_interval)-1):
                    mat[0,x+1]='%.1f-%.1f' % (X_interval[x],X_interval[x+1])
                mat[0,-1]='Total'
                for y in range(0,len(Y_interval)-1):
                    mat[y+1,0]='%.1f-%.1f' % (Y_interval[y],Y_interval[y+1])
                mat[-1,0]='Total'
                # mat[1:,0]=Y_interval[:-1]
                mat[1:,1:]=np.round(occurrence,2).astype(str)
                create_table(output_name,identifiers[j],mat)

    def comparison_stats(measured='measured',hindcast='hindcast',args={'folder out':'/tmp/'}):
        '''function out=comparison_stat(varargin)
                        % % Input:
                        % %     Hindcast data
                        % %     Measured data
                        % %     Output:
                        % % Function:
                        % %     Do a comparison btw hindcast data and measured dta
                        % % Output: 
                        % %     MAE
                        % %     RMSE
                        % %     MRAE
                        % %     BIAS'''

            
        output_name=os.path.join(args['folder out'])

        hindcast=self.data[hindcast].values
        measured=self.data[measure].values
        gd=~np.isnan(hindcast) and ~np.isnan(measured)
        stats=np.empty((4,3),dtype="object")
        stats[0,0]='MAE'
        stats[1,0]='RMSE'
        stats[2,0]='MRAE'
        stats[3,0]='BIAS'
        stats[4,0]='SI'
        stats[5,0]='IOA'
        stats[0,1]='Mean Absolute Error'
        stats[1,1]='Root Mean Square Error'
        stats[2,1]='Mean Relative Absolute Erro'
        stats[3,1]='BIAS'
        stats[4,1]='Scatter Index'
        stats[5,1]='Index of Agreement'


        stats[0,2]='%.2f' % np.mean(np.abs(hindcast[gd]-measured[gd])) #Mean absolute error: 
        stats[1,2]='%.2f' % np.sqrt(np.mean(hindcast[gd]-measured[gd])**2) #%RMS error
        stats[2,2]='%.2f' % np.mean(np.abs((hindcast[gd]-measured[gd])/measured[gd])) #%MRAE
        stats[3,2]='%.2f' % np.mean((hindcast[gd]-measured[gd])) #BIAS
        stats[4,2]='%.2f' % np.sqrt(np.mean(hindcast[gd]-measured[gd])**2)/np.mean(measured[gd]) #SI

        stats[5,2]='%.2f' % 1-(np.sum((np.abs(hindcast-measured))**2))/\
                            (np.sum((np.abs(hindcast-np.mean(measured))+np.abs(measured-np.mean(measured)))**2))        


        create_table(output_name,'comparison stats',stats)