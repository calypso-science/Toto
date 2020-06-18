from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT as NavigationToolbar)

from .message import *

import numpy as np
import copy

# Matplotlib canvas class to create figure
class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig1 = fig#.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class Plotting(object):

    def __init__(self,mplvl,plot_name):
        self.mplvl=mplvl
        self.plot_name=plot_name
        self.addmpl()

    def addmpl(self):
        self.sc = MplCanvas(self, width=50, height=4, dpi=100)
        self.mplvl.addWidget(self.sc)

        self.toolbar = NavigationToolbar(self.sc, 
                 self.mplvl.parent().parent(), coordinates=True)
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
                    print(index_name)

                    self.add_metadata(ax1f1,data[file]['metadata'][index_name],data[file]['metadata'][var])
                elif 'rose'==plot_name:
                    pass
                    # ax = WindroseAxes.from_ax(ax1f1)
                    # ax.bar(x, y)#, normed=True, opening=0.8, edgecolor='white')
                    # ax.set_legend()

                else:
                    plot_ft=getattr(ax1f1, plot_name)
                    plot_ft(x,y,label=var)
                    self.add_metadata(ax1f1,data[file]['metadata'][index_name],data[file]['metadata'][var])
                index_name0=copy.deepcopy(index_name)

    def add_metadata(self,ax,Xmetadata=None,Ymetadata=None):

        if Ymetadata:
            ax.set_ylabel(" %s [%s] " % (Ymetadata['long_name'],Ymetadata['units']))
        if Xmetadata:
            ax.set_xlabel(" %s [%s] " % (Xmetadata['long_name'],Xmetadata['units']))
        ax.legend()
