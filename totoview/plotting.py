import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT as NavigationToolbar)

from PyQt5.QtGui import QIcon

from .message import *

import numpy as np
import copy

from windrose import WindroseAxes

from matplotlib.widgets import RectangleSelector
from matplotlib.axes import SubplotBase
from matplotlib.dates import date2num,num2date
from datetime import datetime
import pandas as pd
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

    def __init__(self, ax, xcollection,ycollection,gid,parent):
        self.ax=ax
        self.canvas = ax.figure.canvas
        self.x = xcollection
        self.y = ycollection
        self.parent=parent
        self.gid=gid

        self.lasso = RectangleSelector(ax, onselect=self.onselect)
        self.ind = []

    def onselect(self, eclick, erelease):

        if self.parent._active == "ZOOM" or self.parent._active == "PAN":
                return


        for i in range(0,len(self.x)):
            Y=self.y[i]
            gid=self.gid[i]
            X=self.x[i]
            if isinstance(X[0],np.datetime64):
                X=date2num(X)



            self.ind =np.nonzero(((X>=eclick.xdata) & (X<=erelease.xdata))\
                & ((Y>=eclick.ydata) & (Y<=erelease.ydata)))[0]

            x_data=X[self.ind]
            y_data=Y[self.ind]

            
            self.ax.plot(x_data,y_data,'r+',gid='selected_'+gid)
        self.ax.set_xlim(X[0],X[-1])
    def disconnect(self):
        self.lasso.disconnect_events()
        self.canvas.draw_idle()

class MyCustomToolbar(NavigationToolbar): 
    def __init__(self, plotCanvas,parent,coordinates):
        NavigationToolbar.__init__(self, plotCanvas,parent,coordinates)
        iconDir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
            "..", "_tools", "")
        self.plotCanvas=plotCanvas
        self.addSeparator()
        self.a = self.addAction(QIcon(iconDir + "select.png"),
            "Select data", self.select_data)
        self.a.setToolTip("Select data")

    def remove_series(self,id='selected'):
        for child in self.plotCanvas.fig1.get_children():
            if child.get_gid() == 'ax':
                lines = [line for line in child.lines if line.get_gid() and line.get_gid().startswith(id)]
                for line in lines:
                    child.lines.remove(line)


    def select_data(self):
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

        self.selector = SelectFromCollection(child, x,y,gid,self)    


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

                
                plot_name=str(self.plot_name.currentText())
                if 'hist'==plot_name:
                    # the histogram of the data
                    ax1f1.hist(y, density=1)
                    self.add_metadata(ax1f1,Xmetadata=data[file]['metadata'][var],Ymetadata=None)
                elif 'progressif'==plot_name:
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
 
                    self.add_metadata(ax1f1,data[file]['metadata'][index_name],data[file]['metadata'][var])
                elif 'rose'==plot_name:
                    if index_name=='time':
                        display_error('Index can not be time')
                        continue
                    self.sc.fig1.clf()
                    ax = WindroseAxes.from_ax(fig=self.sc.fig1)
                    ax.bar(x, y, normed=True, opening=0.8, edgecolor='white')                   
                    ax.set_legend(units=data[file]['metadata'][var]['units'])


                else:
                    ax1f1.set_gid('ax')
                    plot_ft=getattr(ax1f1, plot_name)
                    plot_ft(x,y,label=var,gid=file+';'+var)
                    self.add_metadata(ax1f1,data[file]['metadata'][index_name],data[file]['metadata'][var])
                    if index_name=='time':
                        self.sc.fig1.autofmt_xdate()
                index_name0=copy.deepcopy(index_name)


    def add_metadata(self,ax,Xmetadata=None,Ymetadata=None):

        if Ymetadata:
            ax.set_ylabel(" %s [%s] " % (Ymetadata['long_name'],Ymetadata['units']))
        if Xmetadata:
            ax.set_xlabel(" %s [%s] " % (Xmetadata['long_name'],Xmetadata['units']))
        ax.legend()

