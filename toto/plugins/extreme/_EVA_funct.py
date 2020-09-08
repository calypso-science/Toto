import numpy as np
import sys
try:
    import wafo
    wafo.plotbackend.plotbackend.interactive(False)
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


def get_mag_for_water_elevation(el_res,et,threshold):
        #for seasonal and monthly EVA, the JP tide/surge should account for any
        #tide level (not only the tide corresponding to the selected month/season)
        ntime=np.ceil(len(et)/len(el_res))
        el_resJP=repmat(el_res,int(ntime),1).ravel()
        el_resJP=el_resJP[:len(et)]

        #joint prob tide/surge
        d=0.01;
        jp,X_interval,Y_interval=joint_prob_annual(el_resJP,et,d,d);
        X=np.array([])
        Y=np.array([])
        n=0#%transforms the 2D joint prob into a 1D prob in term of total sea level
        for i in range(0,len(X_interval)-1):
            for j in range(0,len(Y_interval)-1):
                if jp[j,i]!=0:
                    X=np.append(X,X_interval[i]+Y_interval[j]+d)
                    Y=np.append(Y,jp[j,i])
                    n=n+1

        ss=np.arange(0,max(X)+d,d)
        f=np.ones((len(ss)-1,))*np.nan
        for i in range(0,len(ss)-1):
            f[i]=np.sum(Y[np.logical_and(X>=ss[i],X<ss[i+1])])


        ss=ss[:-1]+d/2.
        F=np.cumsum(f)/np.sum(f)
        
        ind=(F>threshold/100).nonzero()[0][0]
        ss=ss[ind:]
        F=F[ind:]
        f=np.diff(F)
        multiplicator = 1./np.min(f[f!=0])  #n_events/(1-F(1));
        mag=np.array([])
        for i in range(0,len(ss)-1):# create
            mag=np.append(mag,ss[i+1]-d/2+d*np.random.rand(int(np.round(np.sqrt((f[i]*multiplicator)))),1))

        return mag
        


def joint_prob_annual(Xdata,Ydata,dx,dy):

    X_interval=np.arange(np.round(min(Xdata),2)-dx,np.round(max(Xdata),2)+dx,dx)
    Y_interval=np.arange(np.round(min(Ydata),2)-dy,np.round(max(Ydata),2)+dy,dy)

    occurrence=np.zeros((len(Y_interval)-1,len(X_interval)-1))
    for k in range(0,len(X_interval)-1):
        index1=np.logical_and(Xdata > X_interval[k],Xdata <= X_interval[k+1])
        for m in range(0,len(Y_interval)-1):
            index2=(np.logical_and(Ydata[index1]>Y_interval[m],Ydata[index1]<=Y_interval[m+1])).nonzero()[0]
            occurrence[m,k]=len(index2)/len(Xdata)

    return occurrence,X_interval,Y_interval

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