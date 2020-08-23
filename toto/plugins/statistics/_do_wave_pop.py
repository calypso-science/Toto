import numpy as np
import copy
from scipy.special import erf
from numpy.matlib import repmat
from ...core.make_table import create_table

def do_wave_pop(time,Hs,Tm,Drr,Tp,Sw,method,dh,Ddir,tbins,exposure,drr_switch,fileout):
    directional_interval=copy.deepcopy(Ddir)
    if method=='Height only':
        N='_Mag'
        method=1
    elif method=='Height/Direction':
        N='_Mag_Dir'
        method=2
    elif method=='Height/Tp':
        N='_Mag_Tp'
        method=3
    elif method=='Height/period':
        N='_Mag_Tm'
        method=4
    else:
        return 'Method unknown'

    dt=(time[2]-time[1]).seconds
    print(method)
    sheetname=N
    if method == 1:
        import pdb;pdb.set_trace()
        if Sw is None:
            pop,hbins,dbins=wavepop(Hs,Tm,dt,dh,method)
            pop,hbins=update_pop(pop,hbins,len(Hs),dt,exposure)
            export_table(fileout,sheetname,pop,hbins,dbins)
        else:
            pop,hbins,dbins=wavepop(Hs,Tm,dt,dh,method,**{'Sw':Sw})
            pop,hbins=update_pop(pop,hbins,len(Hs),dt,exposure)
            export_table(fileout,sheetname,pop,hbins,dbins)
        
    else: 
        if method==2:
            if Drr is None:
                return 'Please make sure you selected the direction time series in the first window'
        elif method == 3 | method==4: #replace direction by period
            if method==3 & Tp==None:
                return 'Please make sure you selected the Tp time series in the first window'
            if method==4 & Sw==None:
                return 'Please make sure you selected the spectral width (SW) time series in the first window'
            drr = Tp.copy()
            if len(tbins)>1:
                Ddir = tbins
            else:
                Ddir=np.arange(0,25+tbins,tbins)
        
        if Sw is None:
            if drr_switch:
                for j in range(0,len(directional_interval)):
                    if j==len(directional_interval)-1:
                        index=np.arange(0,len(Hs),1)
                    else:
                        if directional_interval[j+1] <= directional_interval[j]:
                            index=(Drr>directional_interval[j]) | (Drr<=directional_interval[j+1])
                        else:
                            index=(Drr>directional_interval[j]) & (Drr<=directional_interval[j+1])
                    
                    hs=copy.deepcopy(Hs)
                    hs[~index]=np.NaN;
                    tm=copy.deepcopy(Tm)
                    tm[~index]=np.NaN;
                    drr=copy.deepcopy(Drr)
                    drr[~index]=NaN;
                    
                    pop,hbins,dbins=wavepop(hs,tm,dt,dh,method,drr,Ddir)
                    pop,hbins=update_pop(pop,hbins,len(Hs),dt,exposure)
                    export_table(fileout,sheetname,pop,hbins,dbins)
        
            else:
                pop,hbins,dbins=wavepop(Hs,Tm,dt,dh,method,Drr,Ddir)
                pop,hbins=update_pop(pop,hbins,len(Hs),dt,exposure)
                export_table(fileout,sheetname,pop,hbins,dbins)
            
            
        elif  Sw is not None:
            pop,hbins,dbins=wavepop(Hs,Tm,dt,dh,method,**{'dp':Drr,'ddir':Ddir,'Sw':Sw})
            pop,hbins=update_pop(pop,hbins,len(Hs),dt,exposure)
            export_table(fileout,sheetname,pop,hbins,dbins)
        


def export_table(filename,sheetname,pop,hbins,dbins):
    mat=np.empty((pop.shape[0]+1,pop.shape[1]+1),dtype = "object")
    mat[0,0]=' '
    for x in range(0,len(dbins)-1):
        mat[0,x+1]='%.1f to %.1f' % (dbins[x],dbins[x+1])
    mat[0,-1]='Omni'
    for y in range(0,len(hbins)-1):
        if y != len(hbins)-2:
            mat[y+1,0]='> %.1f <= %.1f' % (hbins[y],hbins[y+1])
        else:
            mat[y+1,0]='Total'

    
    mat[1:,1:]=np.round(pop,2).astype(str)
    create_table(filename,sheetname,mat)




def update_pop(pop,hbins,len,dt,exposure):

    if exposure!=0:
       pop=pop*exposure/(dt*len/(3600*24*365.25));
    

    pop=np.round(pop);

    if pop.shape[1]!=1:
        pop2 = np.zeros((pop.shape[0],pop.shape[1]+1))
        pop2[:,:-1] = pop
        pop2[:,-1]=np.sum(pop,1)
    else:
        pop2=pop
    

    
    #while all(pop(end,:)==0)
    #     pop(end,:)=[];
    #     hbins(end)=[];
    
    pop3=np.zeros((pop2.shape[0]+1,pop2.shape[1]))
    pop3[:-1,:]=pop2
    pop3[-1,:]=np.sum(pop2,0);
    return pop3,hbins


def wavepop(hs,tm,dt,dh,method,**varargin):
    '''wavepop: calculates a population of wave heights in bins of height and
    %         (optionally) direction
    %
    %pop=wavepop(hs,tm,dt,dh,{dp,ddir,SW})
    %
    %%%%%%INPUTS
    %hs         significant wave height
    %tm         mean period (zero crossing period - ~Tm02)
    %dt         time for which hs and tp are representative (in seconds)
    %
    %dh         size of wave height classification bins i.e. 0.25 gives 0-0.25,0.25-0.5 etc.
    %           or vector of bin edges e.g. [0 0.25 0.5 1.0 2.0];
    %method     1= height only, 2= height / direction, 3= height / Tp, 4=
    %           height / period'.
    %dp         optional input for the peak/mean direction (or period) of each sample
    %ddir       if dp specified - size of direction (or period) bins or bin edges
    %SW         optional - spectral width for LH distribution. if iswmpty(SW)=>
    %           uses Rayleigh distribution. 
    % 
    %%%%%%OUTUTS
    %pop        total number of waves in each bin- this is a vector for each height bin
    %           or a matrix if directions or period are specified
    %hbins      vector of wave height bin edges
    %dbins      vector of wave direction (or period if method == 3 or 4) bin edges 

    %Currently uses standard rayleigh distribution or Longuet-Higgins83 (is SW supplied) and assumes:
    %1. Total number of waves is the total time divided by mean period
    %2. All waves in a sample have the same peak/mean direction '''

    #total number of waves for each sample
    hs=hs.flatten()
    tm=tm.flatten()
    nw=(dt/tm).astype('float32')

    if 'dp' in varargin:
        dp=varargin['dp'].flatten()
        ddir=varargin['ddir'];
    else:
        dp=np.zeros((nw.shape))
        if method==4:
            ddir=varargin['ddir']
        else:
            ddir=[0,360]


    if 'sw' in varargin:
        sw=varargin['sw'].flatten()
        typ=2
    elif  'dp' in varargin:
        sw=varargin['dp']
        sw=sw.flatten()
        typ=2
    else:
        typ=1


    #construct bin edges for wave height classifiction
    if isinstance(dh,float):
        hbins=np.arange(0,np.max(3.0*hs)+dh,dh)
    else:
        hbins=dh

    if method == 4:
        tbins=copy.deepcopy(ddir)

    #construct bin edges for wave direction
    if len(ddir)==1:
        x=360./np.round(360./ddir)
        dbins=np.arange(0,360+x,x)
        dbins=np.mod(dbins-ddir/2,360)#centred in the middle of each bin
    else:
        dbins=copy.deepcopy(ddir)

    #assign each sample to a directional bin
    inbin=np.empty(shape=(len(dbins)-1,len(dp)),dtype=bool)
    for i in range(0,len(dbins)-1):
        if dbins[i] > dbins[i+1]:
            inbin[i,:]=((dp>=dbins[i]) | (dp<dbins[i+1]))
        else:
            inbin[i,:]=((dp>=dbins[i]) & (dp<dbins[i+1]))
        

    if typ==2 and method==4:
        cumprob=np.zeros((len(hbins)-1,len(nw),len(tbins)-1))
    else:
        cumprob=np.zeros((len(hbins),len(nw)))

    if typ==1:
        for i in range(1,len(hbins)):
            #cumulative probability wave height is less than upper edeg of bin
            cumprob[i-1,:]=1-np.exp(-2*(hbins[i]/hs)**2)
        
    else:
        if method==4: #2D join-probability distribution
            if len(hs)*len(tbins)*len(hbins)>300000000:
                return 'Please increase bin sizes or time intervals to avoid crashing Matlab'
            cumprob=LH_2D(hbins[1:],tbins[1:],hs,sw,tm)
        else: # %1D probability distribution
            cumprob[1:len(hbins),:]=LH(hbins[1:],hs,sw);  #note here that cumprob(i,:)
            #represents a time series of probability density for h=hbins(i) (not cumulative prob)

    if typ==2 and method==4:
        tmp=np.tile(np.sum(np.sum(cumprob,0),1),(cumprob.shape[0],cumprob.shape[2],1))
        prob_in_bin=cumprob/np.transpose(tmp,(0,2,1))
        prob_in_bin[np.isnan(prob_in_bin)]=0 #just in case we have 0/0 = NaN
        del cumprob

        nw[np.isnan(nw)]=0
        #do it for each wave bins instead of full 3d matrix to avoid crashing
        nw=repmat(nw.T,prob_in_bin.shape[2],1)
        pop=np.zeros((prob_in_bin.shape[0],prob_in_bin.shape[2]))
        #w = waitbar(0,'Summing number of waves for each wave bin');
        for i in range(0,prob_in_bin.shape[0]):
        #%  nw=repmat(nw,[1 1 size(prob_in_bin,3)]);
            pop[i,:]=(np.sum(np.squeeze(prob_in_bin[i,:,:])*nw.T))
        #     waitbar(i/size(prob_in_bin,1));
        # close(w)
    else:

        pop=np.empty((len(hbins)-1,len(dbins)-1))
        if typ==2:#%this has to be done for type 2 to obtain a normalised cumulative probability
            for k in range(0,len(hs)):
                cumprob[:,k]=np.cumsum(cumprob[:,k])/np.sum(cumprob[:,k])
        
        for i in range(1,len(hbins)):
            #subtract previous cumulative probability to get probability in height bin(i)
            prob_in_bin=cumprob[i,:]-cumprob[i-1,:];
            prob_in_bin=prob_in_bin.flatten()
            #multiply by number of waves in each sample, sum and assign to the
            #correct directional bin(j)
            for j in range(1,len(dbins)):
                pop[i-1,j-1]=np.nansum(prob_in_bin[inbin[j-1,:]]*nw[inbin[j-1,:]])

    return pop,hbins,dbins

def LH(h,HS,SW):
    #1D probability density for wave height taking into account spectral width
    #see LONGUET-HIGGINS 1983 p.247
    prob=[];
    while len(HS)>0:
        ind=min(5000,len(HS));#to deal with less data and avoid crashing
        hs=HS[:ind]
        v=SW[:ind] #LONGUET-HIGGINS 1983 abstract SW=sqrt(m0*m2/m1^2-1)
        HS=np.delete(HS,np.arange(0,ind))
        SW=np.delete(SW,np.arange(0,ind))
        
        #first estimate the shift in the distribution compared to rayleigh
        L=1./(0.5*(1+(1+v**2)**-0.5))#LONGUET-HIGGINS 1983 eq. 2.18;
        n=len(L)
        r=np.arange(0,4.01,.01)
        m=len(r)
        #
        F0=.5*(erf(repmat(r,n,1)/repmat(v,m,1).T)+1)#LONGUET-HIGGINS 1983 eq. 5.5 (integrated)
        p=2*repmat(r,n,1)*np.exp(-repmat(r,n,1)**2)*repmat(L,m,1).T*F0#%LONGUET-HIGGINS 1983 eq. 5.4
        p[np.isnan(p)]=0

        P=np.cumsum(p,1)/repmat(np.sum(p,1),m,1).T
        #estimates the ratio r_check to account for the shift from the
        #rayleigh distribution
        Phs=P.T>=2/3
        idx=np.argmax(Phs[:,0])
        #import pdb;pdb.set_trace()
        r_check=np.array(r[idx])
        r_check[r_check==0]=np.nan
        #Shift ratio compared to Rayleigh where Hm0=1.05*Hs.
        r_check=r_check.flatten()/1.05
        m=len(h)
        R=np.sqrt(2)*repmat(h.T,n,1)/repmat((hs*r_check),m,1).T#;%LONGUET-HIGGINS 1983 eq 2.12. Note that R is
        #expressed in term of wave heigth h (rho=h/2 in Longuet-Higgins' paper)
        #slightly non-Rayleigh distribution (as illustrated in fig 2 of LONGUET-HIGGINS 1983)
        F=.5*(erf(R/repmat(v,m,1).T)+1)#;%LONGUET-HIGGINS 1983 eq. 5.5 (integrated)
        prob.append(2*R*np.exp(-R**2)*repmat(L,m,1).T*F)#;%LONGUET-HIGGINS 1983 eq. 5.4

    prob=np.array(prob)
    prob[np.isnan(prob)]=0;
    
    return prob.T.squeeze()

def LH_2D(h,tt,HS,SW,TM):
    #2D probability density for wave height taking into account spectral width
    #see LONGUET-HIGGINS 1983 p.247
    #w = waitbar(0,'Estimating Longuet-Higgins joint probability distributions for each time step');
    len_hs=len(HS)
    while len(HS)>0:
    #    %%%%%%%%%%%%%%%%%%%%%to deal with less data and avoid crashing
        ind=min(500,len(HS))
        hs=HS[:ind]
        v=SW[:ind]#;%LONGUET-HIGGINS 1983 abstract SW=sqrt(m0*m2/m1^2-1)
        tm=TM[:ind]
        HS=np.delete(HS,np.arange(0,ind))
        SW=np.delete(SW,np.arange(0,ind))
        TM=np.delete(TM,np.arange(0,ind))
    #    %%%%%%%%%%%%%%%%%%%%first estimate the shift in the distribution compared to rayleigh
        L=1/(0.5*(1+(1+v**2)**-0.5))#%LONGUET-HIGGINS 1983 eq. 2.18;
        n=len(L)
        r=np.arange(0,4.01,0.01)
        m=len(r)
        F0=.5*(erf(repmat(r,n,1)/repmat(v,m,1).T)+1)#%ONGUET-HIGGINS 1983 eq. 5.5 (integrated)
        p=2*repmat(r,n,1)*np.exp(-repmat(r,n,1)**2)*repmat(L,m,1).T*F0#;%LONGUET-HIGGINS 1983 eq. 5.4
        p[np.isnan(p)]=0
        P=np.cumsum(p,1)/repmat(np.sum(p,1),m,1).T
        Phs=P.T>=2/3
        idx=np.argmax(Phs[:,0])
        r_check=np.array(r[idx])
        r_check[r_check==0]=np.NaN;
        #Shift ratio compared to Rayleigh where Hm0=1.05*Hs.
        r_check=r_check.flatten()/1.05
        o=len(h)
        
        #%%%%%%%%%%%%%%%%%%adjust the normalized wave amplitude R
        R=np.sqrt(2)*repmat(h.flatten().T,n,1)/repmat((hs*r_check),o,1).T#;%LONGUET-HIGGINS 1983 eq 2.12. Note that R is
        #expressed in term of wave heigth h (rho=h/2 in Longuet-Higgins' paper)
        #slightly non-Rayleigh distribution (as illustrated in fig 2 of LONGUET-HIGGINS 1983)
        oo=len(tt);
        T=repmat(tt,n,1)/repmat(tm,oo,1).T#;% T=repmat(tt',1,n)./repmat(tm',oo,1);
        v=np.tile(v,(oo,o,1))
        v=np.transpose(v,(1,2,0))
        L=np.tile(L,(oo,o,1))
        L=np.transpose(L,(1,2,0))
        R=np.tile(R,(oo,1,1)) #8 500 36
        R=np.transpose(R,(2,1,0)) #36 500 8
        T=np.tile(T,(o,1,1))
        #T=np.transpose(T,(2,0,1))
        #%%%%%%%%%%%%%%%%%%%finaly estimate to joint prob distribution: LONGUET-HIGGINS 1983 eq. 2.16 
        if 'prob' not in locals():
            prob=((2./(np.pi**.5*v)*(R**2./T**2))*np.exp(-R**2*(1+v**(-2)*(1-T**-1)**2))*L).astype('float32')
        else:
            tmp=((2/(np.pi**.5*v)*(R**2./T**2))*np.exp(-R**2.*(1+v**(-2)*(1-T**-1)**2))*L).astype('float32')
            prob=np.concatenate((prob,tmp),1)


    prob[np.isnan(prob)]=0
    return prob
