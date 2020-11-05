import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT as NavigationToolbar)

from PyQt5.QtGui import QIcon


from .message import *

import numpy as np
from scipy.signal import find_peaks
import copy

from windrose import WindroseAxes

from matplotlib.widgets import RectangleSelector,SpanSelector
from matplotlib.axes import SubplotBase
import matplotlib.pyplot as plt

#plt.style.use("bmh")
import mplcyberpunk


from matplotlib.dates import date2num,num2date,DateFormatter,AutoDateFormatter,AutoDateLocator
from datetime import datetime
import pandas as pd

from toto.core.toolbox import uv2spdir,spdir2uv

from .CustomDialog import CalendarDialog,PeaksDialog

import matplotlib.dates as mpld
import six

#mpld.set_epoch('0000-12-31T00:00:00')
                    
class SelectFromCollection(object):
    """Select indices from a matplotlib collection using `LassoSelector`.

    Selected indices are saved in the `ind` attribute. This tool highlights
    selected points by fading them out (i.e., reducing their alpha values).
    If your collection has alpha < 1, this tool will permanently alter them.

    Note that this tool selects collection objects based on their *origins*
    (i.e., `offsets`).

    Parameters
    ----------
    ax : :class:`~matplotlib.axes.Axes`
        Axes to interact with.

    collection : :class:`matplotlib.collections.Collection` subclass
        Collection you want to select from.

    alpha_other : 0 <= float <= 1
        To highlight a selection, this tool sets all selected points to an
        alpha value of 1 and non-selected points to `alpha_other`.
    """

    def __init__(self, ax, xcollection,ycollection,gid,parent,method):
        self.ax=ax
        self.canvas = ax.figure.canvas
        self.x = xcollection
        self.y = ycollection
        self.parent=parent
        self.gid=gid

        if method == 'manual':
            self.lasso = RectangleSelector(ax, onselect=self.onselect)
        elif method == 'time':
            w = CalendarDialog(self.ax.get_xlim())
            values = w.getResults()
            if values:
                xmin=datetime(values[0][0],values[0][1],values[0][2])
                xmax=datetime(values[1][0],values[1][1],values[1][2])
                self.selector(lim=[date2num(xmin),date2num(xmax),-np.inf,np.inf])
                self.canvas.draw_idle()
        elif method == 'peaks':
            w = PeaksDialog()
            values = w.getResults()
            self.selector(peaks=values)
            self.canvas.draw_idle()

        elif method == 'spanselector':

            self.span = SpanSelector(
                ax,
                self.printspanselector,
                "horizontal",
                useblit=True,
                rectprops=dict(alpha=0.5, facecolor="red"),
            )
            self.canvas.draw_idle()

        self.ind = []

    def printspanselector(self, xmin, xmax):
        for child in self.parent.plotCanvas.fig1.get_children():
            if child.get_gid() == 'ax':
                objs=child.get_children()

        statf=['mean','min','max',[25,50,75]]
        mat=[]
        columnName=[]
        for stat in statf:
            if isinstance(stat,str):
                columnName.append(stat)
            elif isinstance(stat,list):
                for p in stat:
                    columnName.append('P'+str(p))


        rowName=[]
        color=[]
        for i in range(0,len(self.x)):
            gid=self.gid[i]
            for obj in objs:
                if hasattr(obj,'get_xydata') and obj.get_gid()==gid:
                    color.append(obj.get_color())
                    break

            Y=self.y[i]
            
            rowName.append(gid)
            row=[]
            X=self.x[i]
            if isinstance(X[0],np.datetime64):
                X=date2num(X)

            ind =np.nonzero(((X>=xmin) & (X<=xmax)))[0]
            for stat in statf:
                if isinstance(stat,str):
                    fct=getattr(np, 'nan'+stat)
                    row.append('%.2f'%fct(Y[ind]))
                elif isinstance(stat,list):
                    perc=list(np.percentile(Y[ind],stat))
                    row+=['%.2f'%x for x in perc]                
            
            mat.append(row)

        tb=self.ax.table(cellText=mat,rowLabels=rowName,colLabels=columnName,loc='top',cellLoc='center') 
        for k, cell in six.iteritems(tb._cells):
            cell.set_edgecolor('black')
            if k[0] == 0 :
                cell.set_text_props(weight='bold', color='w')
                cell.set_facecolor(self.ax.get_facecolor())
            else:
                cell.set_text_props(color=color[k[0]-1])
                cell.set_facecolor(self.ax.get_facecolor())

        #tb._cells[(0, 0)].set_facecolor(self.ax.get_facecolor())
        self.span.set_visible(False)

    def selector(self,lim=None, peaks=None):
        if lim:
            xmin=lim[0]
            xmax=lim[1]
            ymin=lim[2]
            ymax=lim[3]

        for i in range(0,len(self.x)):
            Y=self.y[i]
            gid=self.gid[i]
            X=self.x[i]
            if isinstance(X[0],np.datetime64):
                X=date2num(X)

            if lim:
                self.ind =np.nonzero(((X>=xmin) & (X<=xmax))\
                    & ((Y>=ymin) & (Y<=ymax)))[0]

            if peaks:
                self.ind = find_peaks(Y,**peaks)[0]

            x_data=X[self.ind]
            y_data=Y[self.ind]

            
            self.ax.plot(x_data,y_data,'r+',gid='selected_'+gid)
        self.ax.set_xlim(X[0],X[-1])


    def onselect(self, eclick, erelease):
        # if self.parent._active == "ZOOM" or self.parent._active == "PAN":
        #         return
        self.selector(lim=[eclick.xdata,erelease.xdata,eclick.ydata,erelease.ydata])

    def disconnect(self):
        if hasattr(self,'lasso'):
            self.lasso.disconnect_events()
        self.canvas.draw_idle()

class MyCustomToolbar(NavigationToolbar): 
    def __init__(self, plotCanvas,parent,coordinates):
        NavigationToolbar.__init__(self, plotCanvas,parent,coordinates)
        iconDir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
            "..", "_tools", "").replace('\\library.zip','')
        self.plotCanvas=plotCanvas
        self.addSeparator()
        self.a = self.addAction(QIcon(iconDir + "select.png"),
            "Select data manually", self.select_data('manual'))
        self.a.setToolTip("Select data manually")

        self.b = self.addAction(QIcon(iconDir + "calendar.png"),
            "Select data by dates", self.select_data('time'))
        self.b.setToolTip("Select data by dates")

        self.c = self.addAction(QIcon(iconDir + "ic-activity.png"),
            "Select by peaks", self.select_data('peaks'))
        self.c.setToolTip("Select data by peaks")

        self.d = self.addAction(QIcon(iconDir + "table.png"),
            "Stats by selection", self.select_data('spanselector'))
        self.d.setToolTip("Stats by selection")


    def remove_series(self,id='selected'):
        for child in self.plotCanvas.fig1.get_children():
            if child.get_gid() == 'ax':
                lines = [line for line in child.lines if line.get_gid() and line.get_gid().startswith(id)]
                for line in lines:
                    child.lines.remove(line)


    def select_data(self,method):
        def out():
            app=self.parentWidget().parent().parent()
            if hasattr(self,'selector'):
                self.selector.disconnect()
                self.remove_series('selected')
                del self.selector
                
            x=[]
            y=[]
            gid=[]
            for child in self.plotCanvas.fig1.get_children():
                if child.get_gid() == 'ax':
                    objs=child.get_children()
                    for obj in objs:
                        if hasattr(obj,'get_xydata') and obj.get_gid() is not None:
                            y.append(obj.get_ydata(orig=True))
                            x.append(obj.get_xdata(orig=True))
                            gid.append(obj.get_gid())

            self.selector = SelectFromCollection(child, x,y,gid,self,method)    
        return out
# Matplotlib canvas class to create figure
class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig1 = fig#.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
            # --- Drag and drop


class Plotting(object):

    def __init__(self,mplvl,plot_name):
        self.mplvl=mplvl
        self.plot_name=plot_name
        self.addmpl()

    def addmpl(self):
        self.sc = MplCanvas(self, width=50, height=4, dpi=100)
        self.mplvl.addWidget(self.sc)

        self.toolbar = MyCustomToolbar(self.sc, 
                 self.mplvl.parent().parent(),True)
        self.mplvl.addWidget(self.toolbar)

    def rmmpl(self):
        self.mplvl.removeWidget(self.sc)
        self.sc.close()
        self.mplvl.removeWidget(self.toolbar)
        self.toolbar.close()


    def refresh_plot(self,data,File,Var):

        with plt.style.context("cyberpunk"):

            self.rmmpl()
            self.addmpl()

            self.sc.fig1.clf()

            ax1f1 =self.sc.fig1.add_subplot(111)
            
            index_name0=None
            for i,file in enumerate(File):
                for var in Var[i]:
                    scl_fac=data[file]['metadata'][var]['scale_factor']
                    add_offset=data[file]['metadata'][var]['add_offset']
                    index_name=data[file]['dataframe'].index.name
                    if index_name0:
                        if index_name0!=index_name:
                            display_warning('Variables doesn''t have the same index')
                            continue



                    x=data[file]['dataframe'].index
                    y=((data[file]['dataframe'][var])*scl_fac)+add_offset

                    if hasattr(self.plot_name,'currentText'):
                        plot_name=str(self.plot_name.currentText())
                    else:
                        plot_name='plot'

                    if isinstance(x, pd.MultiIndex):
                        plot_name='pcolor'



                    if 'hist'==plot_name:
                        # the histogram of the data
                        ax1f1.hist(y, density=1)
                        self.add_metadata(ax1f1,Xmetadata=data[file]['metadata'][var],Ymetadata=None)
                    elif 'pcolor' == plot_name:
                        indexes=data[file]['dataframe'].index.names
                        X=data[file]['dataframe'].unstack()[indexes[0]]
                        Y=data[file]['dataframe'].unstack()[indexes[1]].values
                        Z=data[file]['dataframe'].unstack()[var].values
                        ax1f1.set_gid('ax')
                        cf=ax1f1.pcolormesh(date2num(X), Y, Z)
                        locator = AutoDateLocator()
                        date_format = AutoDateFormatter(locator)
                        ax1f1.xaxis.set_major_formatter(date_format)
                        self.sc.fig1.autofmt_xdate()
                        self.sc.fig1.colorbar(cf,ax=ax1f1)
                        self.add_metadata(ax1f1,Xmetadata=data[file]['metadata'][indexes[0]],
                            Ymetadata=data[file]['metadata'][indexes[1]],
                            legend=False)
                    elif 'progressif'==plot_name:
                        if index_name=='time':
                            display_error('Index can not be time')
                            continue
                        X=x.array
                        Y=y.array
                        innX = np.isnan(X)
                        innY = np.isnan(Y)
                        
                        
                        X[innX]=0
                        Y[innY]=0
                        
                        posX = np.cumsum(X)
                        posY = np.cumsum(Y)
                        posX[innX] = np.NaN;  
                        posY[innY] = np.NaN;
                        ax1f1.quiver(posX, posY, X, Y)
     
                        self.add_metadata(ax1f1,data[file]['metadata'][index_name],data[file]['metadata'][var],legend=False)
                    elif 'rose'==plot_name:
                        if index_name=='time':
                            display_error('Index can not be time,must be direction or V')
                            continue


                        self.sc.fig1.clf()
                        ax = WindroseAxes.from_ax(fig=self.sc.fig1)
                        gd_data=~np.isnan(y) | ~np.isnan(x)
                        y=y[gd_data]
                        x=x[gd_data]

                        if any(x<0): # it is U and V
                            y,x=uv2spdir(y.values,x.values)
                        ax.bar(x, y, normed=True, opening=0.8, edgecolor='white')                   
                        ax.set_legend(units=data[file]['metadata'][var]['units'])


                    else:
                        ax1f1.set_gid('ax')
                        plot_ft=getattr(ax1f1, plot_name)
                        plot_ft(x,y,label=var,gid=file+';'+var,linewidth=0.8)
                        #ax1f1.set_xlim(x[0],x[-1])
                        
                        self.add_metadata(ax1f1,data[file]['metadata'][index_name],data[file]['metadata'][var])
                        if index_name=='time':
                            self.sc.fig1.autofmt_xdate()

                        ax1f1.grid(True)
                    index_name0=copy.deepcopy(index_name)


    def add_metadata(self,ax,Xmetadata=None,Ymetadata=None,legend=True):

        if Ymetadata:
            ax.set_ylabel(" %s [%s] " % (Ymetadata['long_name'],Ymetadata['units']))
        if Xmetadata:
            ax.set_xlabel(" %s [%s] " % (Xmetadata['long_name'],Xmetadata['units']))
        if legend:
            ax.legend()

