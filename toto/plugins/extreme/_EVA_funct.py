import numpy as np
import wafo.stats as ws
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
        phat = ws.weibull_min.fit2(mag,f0=loc,method=method.lower(),alpha=0.05)
        scale=phat.par[-1]
        shape=phat.par[1]
    elif fitting.lower() == 'gumbel':
        phat = ws.gumbel_r.fit2(mag,method=method,alpha=0.05)
        scale=phat.par[-1]
        shape=phat.par[0]
    elif fitting.lower() == 'gpd':
        phat = phat.genpareto.fit2(mag,floc=loc,method=method.lower(),alpha=0.05)
        scale=phat.par[-1]
        shape=phat.par[0]

    elif fitting.lower() == 'gev':
        phat = phat.genextreme.fit2(mag,floc=loc,method=method.lower(),alpha=0.05)
        scale=phat.par[0]
        shape=phat.par[-1]

    else:
        assert 'Fitting %s not recognize' % fitting

    return phat,scale,shape

def do_ext(kRp,phat,method,LnN=None,):
    if method!= 'isf':
        if (LnN  is None):
            assert 'With this method need LnN'

    if method== 'isf':
        magex=phat.isf(kRp)
    else: # convolution method
        loc=np.nanmin(phat.data)*.999
        x=np.linspace(loc,np.max(phat.data),1000);
        dx=x[1]-x[0]

        P_lt=phat.pdf(x-loc)
        P_lt[np.isinf(P_lt)]=0
        LnN=np.nanmean(LnN);
        
        #convolution method p.390 of TROMANS and VANDERSCHUREN (1995)
        h=np.linspace(0,30,3001) #;% 0.01 precision
        
        X=repmat(x,len(h),1)
        P_LT=repmat(P_lt,len(h),1)
        H=repmat(h,len(x),1).T
        P=np.exp(-np.exp(-LnN * (((H/X)**2 -1 )) )) * P_LT 
        
        P=np.sum(P,1)*dx
        P=P/np.max(P)
        magex=np.ones((len(kRp),))*np.NaN
        for i in range(0,len(kRp)):
            P_poisson_process=P**kRp[i] #% p.390 of TROMANS and VANDERSCHUREN (1995)
            id_last=(P_poisson_process<1/np.exp(1)).nonzero()[0]
            hh=[]
            if len(id_last)>0:
                hh.append(h[id_last[-1]])

            id_first=(P_poisson_process>1/np.exp(1)).nonzero()[0]
            if len(id_first)>0:
                hh.append(h[id_first[0]])

            magex[i]=np.mean(hh)

    return magex
        

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