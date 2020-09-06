import numpy as np
import sys
try:
    import wafo.stats as ws
except:
    print('')
    print('')
    print('Error: problem loading wafo package:')
    print('  - Check if this package is installed ( e.g. type: `pip install pywafo`)')
    print('')
    print('')
    sys.exit(-1)

from numpy.matlib import repmat

def sub_table(stats,varname,rp):
    
    dds= stats.keys()
    rvs=len(rp)
    mat=np.empty((rvs+2,len(dds)+1),dtype = "object")
    mat[0,0]=varname
    for i,dd in enumerate(dds):
        mat[0,i+1]=dd
        mat[1:1+rvs,i+1]=np.round(stats[dd][varname]['magex'],2).astype(str)


    mat[1:1+rvs,0]=np.round(rp).astype(str)
    mat[-1,:]=''
    return mat

def calc_kRp(rp,nval,nlen,Hmp=False):

    if Hmp:
        v=(nval+1)/nlen #mean arrival rate of random storms
        kRp=v*rp;   
    else:

        nstorm_per_year=nval/nlen
        kR=nstorm_per_year*rp
        kR[kR<1.001]=1.001
        kRp=1/kR

    return kRp

def do_fitting(mag,fitting,method,loc=None):
    if loc is None:
        loc=np.nanmin(mag)*.999

    if fitting.lower()=='weibull':
        phat = ws.weibull_min.fit2(mag,floc=loc,method=method.lower(),alpha=0.05)
        scale=phat.par[-1]
        shape=phat.par[0]
    elif fitting.lower() == 'gumbel':
        phat = ws.gumbel_r.fit2(mag,method=method,alpha=0.05)
        scale=phat.par[0]
        shape=phat.par[-1]
    elif fitting.lower() == 'gpd':
        phat = phat.genpareto.fit2(mag,floc=loc,method=method.lower(),alpha=0.05)
        scale=phat.par[-1]
        shape=phat.par[0]*-1

    elif fitting.lower() == 'gev':
        phat = phat.genextreme.fit2(mag,floc=loc,method=method.lower(),alpha=0.05)
        scale=phat.par[-1]
        shape=phat.par[0]

    else:
        assert 'Fitting %s not recognize' % fitting

    return phat,scale,shape


        

if __name__ == "__main__":
    import wafo.data as wd
    Hs = wd.atlantic()
    phat,scale,shape=do_fitting(Hs,'gump','ml')
    nlen=1
    nstorm_per_year=len(Hs)/nlen
    rp=np.array([5])
    kR=max(1.001,nstorm_per_year*rp);
    kRp=1./kR;
    magex=do_ext(kRp,phat,'caca',LnN=[1])
    print(magex)