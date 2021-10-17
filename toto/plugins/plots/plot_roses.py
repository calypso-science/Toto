import pandas as pd
import os
from ._do_roses import do_roses
from ._do_bias_hist import do_bias_hist
from ._do_density_diagramm import do_density_diagramm
from ._do_perc_of_occurence import do_perc_of_occurence
from ._do_qq_plot import qq_plot
from ._thermocline import thermocline
from toto.plugins.statistics._do_joint_prob import _do_joint_prob_plot
from ...core.toolbox import get_opt,dir_interval,get_increment
import numpy as np


@pd.api.extensions.register_dataframe_accessor("StatPlots")
class StatPlots:
    def __init__(self, pandas_obj):
#        self._validate(pandas_obj)
        self.data = pandas_obj
        self.dfout = pd.DataFrame(index=self.data.index.copy())

    def plot_roses(self,mag='mag',drr='drr',\
        args={'title':'Current speed',\
        'units':'m/s',\
        'speed bins (optional)':[],
        '% quadran (optional)':[],
        'time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
        'folder out':os.getcwd(),
        'display':{'On':True,'Off':False}
        }):

        """ This function provides annual, seasonal or monthly rose plots for wind,
            wave, current or any direcional variable.
            This function is using https://github.com/python-windrose/windrose
            
            Parameters
            ~~~~~~~~~~

            mag : str
                Name of the column from which to get stats.
            drr : str
                Column name representing the directions.
            args: dict
                Dictionnary with the folowing keys:
                title: str
                    Graph title
                speed bins (optional): list
                    Speed to plot
                % quadran (optional): list
                    Percentage of each occurence to plot
                display: str
                    `On` or `Off` to display image
                folder out: str
                    Path to save the output
                time blocking: str
                     if ``Time blocking=='Annual'``,
                        Statistics will be calculated for the whole timeserie
                     if ``Time blocking=='Seasonal (South hemisphere)'``,
                        Statistics will be calculated for South hemisphere seasons
                     if ``Time blocking=='Seasonal (North hemisphere)'``,
                        Statistics will be calculated for North hemisphere seasons
                     if ``Time blocking=='Monthly'``,
                        Statistics will be calculated for each month.
   

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].StatPlots.plot_roses(mag='U',drr='drr',args={'time blocking':'Yearly'})
            >>> 
        """

        display=True
        if args.get('display','Off')=='Off':
            display=False
        unit=get_opt(self.data[mag],'units',args['units'])

        if not hasattr(self.data,'filename'):
            self.data.filename=''
        
        filename=os.path.join(args.get('folder out',os.getcwd()),os.path.splitext(self.data.filename)[0]+'_rose_'+mag+'.png')
        do_roses(self.data.index,self.data[mag],self.data[drr],unit,args['title'],
            args['speed bins (optional)'],args['% quadran (optional)'],args['time blocking'],filename,display)



    
    def BIAS_histogramm(self,measured='measured',modelled='modelled',
        args={'Nb of bins':30,'Xlabel':'','units':'','display':{'On':True,'Off':False},'folder out':os.getcwd()}):


        """ This function provides a bias histogramm
            between measured and predicted data for any variables

            Parameters
            ~~~~~~~~~~

            measured : str
                Name of the column to contain the measured data.
            modelled : str
                Name of the column to contain the modelled data.
            args: dict
                Dictionnary with the folowing keys:
                Nb of bins: int
                    Number of bins to use
                Xlabel: str
                    X axis label
                Units: str
                    Units of the data
                display: str
                    `On` or `Off` to display image
                folder out: str
                    Path to save the output

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].StatPlots.BIAS_histogramm(measured='U',modelled='U_m')
            >>> 
        """

        display=True
        if args.get('display','Off')=='Off':
            display=False 

        if not hasattr(self.data,'filename'):
            self.data.filename=''

        filename=os.path.join(args.get('folder out',os.getcwd()),os.path.splitext(self.data.filename)[0]+'_biasHist.png')
        unit=get_opt(self.data[measured],'units',args.get('units',''))

        short_name=get_opt(self.data[measured],'short_name',args.get('Xlabel',''))
        self.data=self.data.dropna()
        do_bias_hist(self.data[measured].values,self.data[modelled].values,unit,short_name,args.get('Nb of bins',30),filename,display)


    def density_diagramm(self,X='X',Y='Y',args={
        'Y name':'',
        'X name':'',
        'Y unit':'',
        'X unit':'',
        'Y limits':[0,np.inf],
        'X limits':[0,np.inf],
        'display':{'On':True,'Off':False},
        'folder out':os.getcwd()}):


        """ This function provides density diagrams of parameter Y vs parameter X,
           i.e. similar to scatter plot but emphasing on region withg large number
           of data

            Parameters
            ~~~~~~~~~~

            X : str
                Name of the column to plot on the X axis.
            Y : str
                Name of the column to plot on the Y axis.
            args: dict
                Dictionnary with the folowing keys:
                Y name: str
                    Name of the Y axis
                X name: str
                    Name of the X axis
                Y unit: str
                    Unit of the Y axis
                X unit: str
                    Unit of the X axis
                Y limits: list
                    2 value list with Y axis limit
                X limits: list
                    2 value list with X axis limits
                display: str
                    `On` or `Off` to display image
                folder out: str
                    Path to save the output

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].StatPlots.density_diagramm(X='U',Y='U_m')
            >>> 
        """

        display=True
        if args.get('display','Off')=='Off':
            display=False
        X_short_name=get_opt(self.data[X],'short_name',args.get('X name',''))
        Y_short_name=get_opt(self.data[Y],'short_name',args.get('Y name',''))

        X_unit=get_opt(self.data[X],'units',args.get('X unit',''))
        Y_unit=get_opt(self.data[Y],'units',args.get('Y unit',''))       

        Xlim=args.get('X limits',[0,np.inf])
        Ylim=args.get('Y limits',[0,np.inf])

        if hasattr(self.data,'filename'):
            filename=os.path.join(args.get('folder out',os.getcwd()),os.path.splitext(self.data.filename)[0]+'_'+X+'_'+Y+'_density_diagramm.png')
        else:
            filename=os.path.join(args.get('folder out',os.getcwd()),'density_diagramm.png')

        do_density_diagramm(self.data[X].values,self.data[Y].values,X_short_name,Y_short_name,X_unit,Y_unit,Xlim,Ylim,filename,display)


    def QQ_plot(self,measured='measured',modelled='modelled',args={
        'measured name':'',
        'modelled name':'',
        'measured unit':'',
        'modelled unit':'',
        'Quantile increment step (%)':1.0,
        'display':{'On':True,'Off':False},
        'folder out':os.getcwd()}):


        """ This function provides Quantile-Quantile plots (Q-Q plots) for comparison
            statistics.

            Parameters
            ~~~~~~~~~~

            measured : str
                Name of the column to contain the measured data.
            modelled : str
                Name of the column to contain the modelled data.
            args: dict
                Dictionnary with the folowing keys:
                measured name: str
                    Name of the Y axis
                modelled name: str
                    Name of the X axis
                measured unit: str
                    Unit of the Y axis
                modelled unit: str
                    Unit of the X axis
                Quantile increment step (%): float
                    Quantile increment step in percentage
                display: str
                    `On` or `Off` to display image
                folder out: str
                    Path to save the output

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].StatPlots.QQ_plot(measured='U',modelled='U_m')
            >>> 
        """

        display=True
        if args.get('display','Off')=='Off':
            display=False
        X_short_name=get_opt(self.data[measured],'short_name',args.get('measured name',''))
        Y_short_name=get_opt(self.data[modelled],'short_name',args.get('modelled name',''))

        X_unit=get_opt(self.data[measured],'units',args.get('measured unit',''))
        Y_unit=get_opt(self.data[modelled],'units',args.get('modelled unit',''))        

        pvec=np.arange(0,100+args.get('Quantile increment step (%)',1),args.get('Quantile increment step (%)',1))
        if not hasattr(self.data,'filename'):
            self.data.filename=''
        filename=os.path.join(args.get('folder out',os.getcwd()),os.path.splitext(self.data.filename)[0]+'_qqplot.png')

        qq_plot(self.data[measured],self.data[modelled],pvec,X_short_name,Y_short_name,X_unit,Y_unit,filename,display)



    def percentage_of_occurence(self,mag='mag',drr='drr',args={
                'magnitude interval (optional)':[],
                'X label':'Wind speed in [m/s]',
                'time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
                'direction binning':{'centered':True,'not-centered':False},
                'direction interval': 45.,
                'display':{'On':True,'Off':False},
                'folder out':os.getcwd()}):

        """ This function provides percentage of occurnce from any variable.
            plot are directional if direction is supplied

            Parameters
            ~~~~~~~~~~

            mag : str
                Name of the column from which to get stats.
            drr : str
                Column name representing the directions.
            args: dict
                Dictionnary with the folowing keys:
                title: str
                    Graph title
                magnitude interval (optional): list
                    interval to use for the magnitude
                X label: str
                    Label for the X axis
                direction binning: str
                    Can be `centered` or `not-centered` depending if the directionnal are centered over 0
                direction interval: int
                    Dirctionnal interval for the bins in degrees
                display: str
                    `On` or `Off` to display image
                folder out: str
                    Path to save the output
                time blocking: str
                     if ``Time blocking=='Annual'``,
                        Statistics will be calculated for the whole timeserie
                     if ``Time blocking=='Seasonal (South hemisphere)'``,
                        Statistics will be calculated for South hemisphere seasons
                     if ``Time blocking=='Seasonal (North hemisphere)'``,
                        Statistics will be calculated for North hemisphere seasons
                     if ``Time blocking=='Monthly'``,
                        Statistics will be calculated for each month.
   

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].StatPlots.Percentage_of_occurence(mag='U',drr='drr',args={'time blocking':'Yearly'})
            >>> 
        """

        display=True
        if args.get('display','Off')=='Off':
            display=False

        if drr in self.data:
            drr=self.data[drr].values
        else:
            drr=None

        mag_inteval=args.get('magnitude interval (optional)',[])
        X_unit=get_opt(self.data[mag],'units','')
        X_short_name=get_opt(self.data[mag],'short_name','')
        if X_short_name=='':
            xlabel=args.get('X label','')
        else:
            xlabel=X_short_name+' ['+X_unit+']'

        if not hasattr(self.data,'filename'):
            self.data.filename=''

        filename=os.path.join(args.get('folder out',os.getcwd()),os.path.splitext(self.data.filename)[0]+'_OccurencePlot.png')

        drr_interval=dir_interval(args['direction interval'],args['direction binning'])
        do_perc_of_occurence(self.data.index,self.data[mag].values,drr,mag_inteval,xlabel,args['time blocking'],drr_interval,filename,display)

    def plot_thermocline(self,mag=['mag'],args={
                'function':{'Max':True, 'Mean':False, 'Median':False, 'Min':False, 'Percentile':False, 'Prod':False, 'Quantile':False, 'Std':False, 'Sum':False, 'Var':False},
                'percentile or Quantile': 0.1,
                'X label':'Water temperature [degC]',
                'time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
                'display':{'On':True,'Off':False},
                'table':{'On':True,'Off':False},
                'folder out':os.getcwd()}):

        """ This function provides a plot of parameter versus water depth.
            This function average the timeseries ( by mean, median ...)

            Notes
            ~~~~~

            Variables MUST be in the format *_lev_1,*_lev_2 etc.. 

            Parameters
            ~~~~~~~~~~

            mag : list
                Name of the column from which to get stats.
            args: dict
                Dictionnary with the folowing keys:
                function: str
                    Statistics to use to process each level:
                    can be `Max`,`Mean`,`Median`,`Min`,`Percentile`,`Prod`,`Quantile`,`Std`,`Sum` or `Var`
                'percentile or Quantile': float
                    Percetile or quantile to use
                X label: str
                    Label for the X axis
                display: str
                    `On` or `Off` to display image
                table: str
                    `On` or `Off` to print result in a table
                folder out: str
                    Path to save the output
                time blocking: str
                     if ``Time blocking=='Annual'``,
                        Statistics will be calculated for the whole timeserie
                     if ``Time blocking=='Seasonal (South hemisphere)'``,
                        Statistics will be calculated for South hemisphere seasons
                     if ``Time blocking=='Seasonal (North hemisphere)'``,
                        Statistics will be calculated for North hemisphere seasons
                     if ``Time blocking=='Monthly'``,
                        Statistics will be calculated for each month.
   

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].StatPlots.plot_thermocline(mag=['U_lev_1','U_lev_2'],args={'function':'Mean',time blocking':'Yearly'})
            >>> 
        """

        if isinstance(mag,str):
            return 'cannot be only one level,select multiple'

        display=True
        if args.get('display','Off')=='Off':
            display=False

        X_unit=get_opt(self.data[mag[0]],'units','')
        X_short_name=get_opt(self.data[mag[0]],'short_name','')
        if X_short_name=='':
            xlabel=args.get('X label','')
        else:
            xlabel=X_short_name+' ['+X_unit+']'


        funct=getattr(np,'nan'+args['function'].lower())
        val=args.get('percentile or Quantile',0.1)
        if not hasattr(self.data,'filename'):
            self.data.filename=''

        table_filename=os.path.join(args.get('folder out',os.getcwd()),os.path.splitext(self.data.filename)[0]+'_thermocline.xlsx')
        figure_filename=os.path.join(args.get('folder out',os.getcwd()),os.path.splitext(self.data.filename)[0]+'_thermocline.png')
        th=thermocline(self.data[mag],time_blocking=args['time blocking'],funct=funct,val=val)
        if args.get('table','Off')=='On':
            th.output_table(table_filename)
        th.output_fig(figure_filename,xlabel=xlabel,display=display)



    def joint_probability_plot(self,X='X',Y='Y',\
        args={    
        'X Min Res Max(optional)':[2,1,22],
        'Y Min Res Max(optional)':[0,0.5],
        'X label':'',
        'Y label':'',
        'time blocking':{'Annual':True,'Seasonal (South hemisphere)':False,'Seasonal (North hemisphere)':False,'Monthly':False},
        'probablity expressed in':{'percent':False,'per thoushand':True},
        'display':{'On':True,'Off':False},
        'folder out':os.getcwd(),
        }):
        """ This function provides joint distribution graph for X and Y, i.e. the
            probability of events defined in terms of both X and Y (per 1000)
        
            Parameters
            ~~~~~~~~~~

            X : str
                Name of the column to plot on the X axis.
            Y : str
                Name of the column to plot on the Y axis.
            args: dict
                Dictionnary with the folowing keys:
                X Min Res Max(optional): list
                    Minimum, resolution and maximum value of X axis use in the join probability
                Y Min Res Max(optional): list
                    Minimum, resolution and maximum value of Y axis use in the join probability
                X label: str
                    Label for the X axis
                Y label: str
                    Label for the Y axis
                display: str
                    `On` or `Off` to display image
                folder out: str
                    Path to save the output
                probablity expressed in:
                    Can be `percent` or `per thoushand`
                time blocking: str
                     if ``Time blocking=='Annual'``,
                        Statistics will be calculated for the whole timeserie
                     if ``Time blocking=='Seasonal (South hemisphere)'``,
                        Statistics will be calculated for South hemisphere seasons
                     if ``Time blocking=='Seasonal (North hemisphere)'``,
                        Statistics will be calculated for North hemisphere seasons
                     if ``Time blocking=='Monthly'``,
                        Statistics will be calculated for each month.
   

            Examples:
            ~~~~~~~~~
            >>> df=tf['test1']['dataframe'].StatPlots.plot_thermocline(mag=['U_lev_1','U_lev_2'],args={'function':'Mean',time blocking':'Yearly'})
            >>> 
        """

        display=True
        if args.get('display','Off')=='Off':
            display=False
        Ydata=self.data[Y]
        Xdata=self.data[X]
        if not hasattr(self.data,'filename'):
            self.data.filename=''
        filename=os.path.join(args.get('folder out',os.getcwd()),os.path.splitext(self.data.filename)[0]+'JP.png')

        if args.get('probablity expressed in','percent')=='percent':
            multiplier=100.
        else:
            multiplier=1000.
        Y_interval=get_increment(Ydata,args.get('Y Min Res Max(optional)',[2,1]))
        X_interval=get_increment(Xdata,args.get('X Min Res Max(optional)',[0,0.5]))

        X_unit=get_opt(self.data[X],'units','')
        X_short_name=get_opt(self.data[X],'short_name','')
        if X_short_name=='':
            xlabel=args.get('X label','')
        else:
            xlabel=X_short_name+' ['+X_unit+']'

        Y_unit=get_opt(self.data[Y],'units','')
        Y_short_name=get_opt(self.data[Y],'short_name','')
        if Y_short_name=='':
            ylabel=args.get('Y label','')
        else:
            ylabel=Y_short_name+' ['+Y_unit+']'

        _do_joint_prob_plot(filename,self.data.index,Xdata,Ydata,X_interval,Y_interval,args['time blocking'],display,xlabel,ylabel,multiplier)
