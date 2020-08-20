
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from scipy.stats import kde

def do_density_diagramm(X,Y,X_short_name,Y_short_name,X_unit,Y_unit,Xlim,Ylim):

    fig = plt.figure(figsize=(8.27, 11.69), dpi=100)
    ax =fig.add_subplot(111)



    ax.set_xlabel(" %s [%s] " % (X_short_name,X_unit))
    ax.set_ylabel(" %s [%s] " % (Y_short_name,Y_unit))

    if not np.isinf(Xlim[-1]):
        ax.set_xlim(Xlim[0],Xlim[-1])
    if not np.isinf(Ylim[-1]):
        ax.set_ylim(Ylim[0],Ylim[-1])

    # Evaluate a gaussian kde on a regular grid of nbins x nbins over data extents
    nbins=300
    k = kde.gaussian_kde([X,Y])
    xi, yi = np.mgrid[X.min():X.max():nbins*1j, Y.min():Y.max():nbins*1j]
    zi = k(np.vstack([xi.flatten(), yi.flatten()]))
 
    # Make the plot
    plt.pcolormesh(xi, yi, zi.reshape(xi.shape))
    plt.colorbar()
    #plt.show()
    plt.savefig(fileout)

