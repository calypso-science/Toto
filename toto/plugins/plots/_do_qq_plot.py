import numpy as np

from matplotlib import pyplot as plt
from matplotlib.figure import Figure

def qq_plot(X,Y,pvec,X_short_name,Y_short_name,Xunit,Yunit,fileout,show=True):


    Y=Y[~np.isnan(Y)]
    X=X[~np.isnan(X)]
    yy=np.percentile(Y,pvec)
    xx=np.percentile(X,pvec)

    fig = plt.figure(figsize=(8.27, 11.69), dpi=100)
    ax =fig.add_subplot(111)

    max_plot=max(np.max(X),np.max(Y))+.1*max(np.max(X),np.max(Y))
    ax.plot(xx,yy,'*')
    ax.plot([0,max_plot],[0,max_plot],'--k')

    
    ax.set_xlim(0,max_plot)
    ax.set_ylim(0,max_plot)

    ax.set_xlabel("Measured %s quantile [%s]" % (X_short_name,Xunit))
    ax.set_ylabel('Modelled %s quantile [%s]'% (Y_short_name,Yunit))
    ylim=ax.get_ylim()
    ax.plot([0,0],[0,max(ylim)],'k--')
    
    plt.savefig(fileout)
    plt.show(block=~show)

