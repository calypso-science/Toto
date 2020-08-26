
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

def do_bias_hist(X,Y,unit,short_name,nbins,filename,show=True):


  BIAS=X-Y #Bias

  a,b = np.histogram(BIAS,nbins) 

  B=np.nanmax(np.abs(b))

  fig = plt.figure(figsize=(8.27, 11.69), dpi=100)
  ax =fig.add_subplot(111)

  plt.step(np.diff(b)+b[:-1],a)
  ax.set_xlim(B*-1,B)

  ax.set_xlabel(" %s Bias [%s] " % (short_name,unit))
  ax.set_ylabel('Datapoints per bin')
  ylim=ax.get_ylim()
  ax.plot([0,0],[0,max(ylim)],'k--')
  plt.show(block=~show)
  plt.savefig(fileout)



