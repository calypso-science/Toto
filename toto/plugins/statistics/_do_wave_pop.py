import numpy as np
import copy
from scipy.special import erf
from numpy.matlib import repmat

def do_wave_pop(time,Hs,Tm,Drr=None,Tp=None,Sw=None,method,dh,Ddir,tbins,exposure,drr_switch,fileout):
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
    elif method=='height/period':
        N='_Mag_Tm'
        method=4
    else:
        return 'Method unknown'

    dt=(time[2]-time[1]).seconds


    if method == 1:
        if Sw==None:
            pop,hbins,dbins=wavepop(Hs,Tm,dt,dh,method)
            pop,hbins=update_pop(pop,hbins,len(Hs),dt,exposure)
            export_table(fileout,sheetname,pop,hbins,dbins)
        else:
            pop,hbins,dbins=wavepop(Hs,Tm,dt,dh,method,Sw)
            pop,hbins=update_pop(pop,hbins,len(Hs),dt,exposure)
            export_table(fileout,sheetname,pop,hbins,dbins)
        
    else: 
        if method==2:
            if Drr==None:
                return 'Please make sure you selected the direction time series in the first window'
        elif method == 3 || method==4: #replace direction by period
            if method==3 & Tp==None:
                return 'Please make sure you selected the Tp time series in the first window'
            if method==4 & Sw==None:
                return 'Please make sure you selected the spectral width (SW) time series in the first window'
            drr = Tp.copy()
            if len(tbins)>1:
                Ddir = tbins
            else:
                Ddir=np.arange(0,25+tbins,tbins)
        
        if Sw==None:
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
                    drr=copy.deepcopy(Dir)
                    drr[~index]=NaN;
                    
                    pop,hbins,dbins=wavepop(hs,tm,dt,dh,method,drr,Ddir)
                    pop,hbins=update_pop(pop,hbins,len(Hs),dt,exposure)
                    export_table(fileout,sheetname,pop,hbins,dbins)
        
            else:
                pop,hbins,dbins=wavepop(Hs,Tm,dt,dh,method,Dir,Ddir)
                pop,hbins=update_pop(pop,hbins,len(Hs),dt,exposure)
                export_table(fileout,sheetname,pop,hbins,dbins)
            
            
        elif  Sw!=None:
            pop,hbins,dbins=wavepop(Hs,Tm,dt,dh,method,Dir,Ddir,SW)
            pop,hbins=update_pop(pop,hbins,len(Hs),dt,exposure)
            export_table(fileout,sheetname,pop,hbins,dbins)
        


    def export_table(filename,sheetname,pop,hbins,dbins)
        mat=np.empty((pop.shape[0]+1,pop.shape[1]+1),dtype = "object")
        mat[0,0]=' '
        for x in range(0,len(dbins)-1):
            mat[0,x+1]='%.1f to %.1f' % (X_interval[x],X_interval[x+1])
        mat[0,-1]='Omni'
        for y in range(0,len(hbins)):
            if y != len(hbins)-2:
                mat[y+1,0]='> %.1f <= %.1f' % (hbins[y],hbins[y+1])
            else:
                mat[y+1,0]='Total'

        
        mat[1:,1:]=np.round(pop,2).astype(str)
        create_table(filename,identifiers[j],mat)




    def update_pop(pop,hbins,len,dt,exposure):

        if exposure!=0:
           pop=pop*exposure/(dt*len/(3600*24*365.25));
        

        pop=np.round(pop);
        if pop.shape[1]~=1:
            pop2 = np.zeros((pop.shape[0],pop.shape[1]+1))
            pop2[:,:-1] = pop
            pop2[:,-1]=np.sum(pop,1)
        

        while all(pop(end,:)==0)
            pop(end,:)=[];
            hbins(end)=[];
        
        pop3=np.zeros((pop2.shape[0]+1,pop2.shape[1]))
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
nw=(dt/tm).astype(float32)

if 'dp' in varargin:
    dp=varargin['dp'].flatten()
    ddir=varargin{2};
else:
    dp=np.zeros((nw.shape))
    if method==4:
        ddir=varargin['ddir']
    else:
        ddir=[0,360]


if nargin==8 && ~isempty(varargin{3})
    sw=varargin['sw'].flatten()
    typ=2
elif  nargin==6 && ~isempty(varargin{1})
    sw=varargin{1};sw=sw(:);type=2;
else:
    typ=1


#construct bin edges for wave height classifiction
if len(dh)==1:
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
inbin=np.array((len(dbins)-1,1))
for i in range(0,len(dbins)-1):
    if dbins[i] > dbins[i+1]:
        inbin[i]=((dp>=dbins[i]) | (dp<dbins[i+1])).nonzeros()[0]
    else:
        inbin[i]=((dp>=dbins[i]) & (dp<dbins[i+1])).nonzeros()[0]
    

if typ==2 and method==4:
    cumprob=np.zeros(len(hbins)-1,nw.shape[0],nw.shape[1],len(tbins)-1)
else:
    cumprob=np.zeros((1,nw.shape[0],nw.shape[1]))

if typ==1
    for i in range(1:len(hbins)):
        #cumulative probability wave height is less than upper edeg of bin
        cumprob[i,:]=1-np.exp(-2*(hbins[i]./hs)**2)
    
else:
    if method==4: #2D join-probability distribution
        if len(hs)*len(tbins)*len(hbins)>300000000:
            return 'Please increase bin sizes or time intervals to avoid crashing Matlab'
       cumprob=LH_2D(hbins[1:],tbins[1:],hs,sw,tm)
    else: # %1D probability distribution
        cumprob[1:len(hbins),:]=LH(hbins[1:],hs,sw);  #note here that cumprob(i,:)
        #represents a time series of probability density for h=hbins(i) (not cumulative prob)

if typ==2 && method==4:
    prob_in_bin=cumprob./np.repmat(np.sum(np.sum(cumprob,1),3),(cumprob.shape[0],1,cumprob.shape[2]))
    prob_in_bin[np.isnan(prob_in_bin)]=0 #just in case we have 0/0 = NaN
    del cumprob

 nw[np.isnan(nw)]=0
 #do it for each wave bins instead of full 3d matrix to avoid crashing
 nw=np.repmat(nw.T,(prob_in_bin.shape[2],1))
 pop=zeros((prob_in_bin.shape[0],prob_in_bin.shape[2]))
 #w = waitbar(0,'Summing number of waves for each wave bin');
 for i in range(0,prob_in_bin.shape[0]):
#%  nw=repmat(nw,[1 1 size(prob_in_bin,3)]);
    pop[i,:]=(np.sum(np.squeeze(prob_in_bin[i,:,:]).*nw.T))
#     waitbar(i/size(prob_in_bin,1));
# close(w)
else:
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
            pop[i-1,j-1]=np.nansum(prob_in_bin[inbin[j-1]].*nw[inbin[j-1]])

return pop,hbins,dbins

def LH(h,HS,SW)
#1D probability density for wave height taking into account spectral width
#see LONGUET-HIGGINS 1983 p.247
prob=[];
while ~np.isempty(HS):
    ind=min(5000,length(HS));#to deal with less data and avoid crashing
    hs=HS[:ind]
    v=SW[:ind] #LONGUET-HIGGINS 1983 abstract SW=sqrt(m0*m2/m1^2-1)
    HS[:ind]=[];
    SW[:ind]=[];
    
    #first estimate the shift in the distribution compared to rayleigh
    L=1./(0.5*(1+(1+v**2)**-0.5))#LONGUET-HIGGINS 1983 eq. 2.18;
    n=len(L)
    r=np.arange(0,4.01,.01)
    m=len(r)
    F0=.5*(erf(np.repmat(r,(n,1))/np.repmat(v,(1,m)))+1)#LONGUET-HIGGINS 1983 eq. 5.5 (integrated)
    p=2*np.repmat(r,(n,1))*np.exp(-np.repmat(r,(n,1))**2)*np.repmat(L,(1,m))*F0#%LONGUET-HIGGINS 1983 eq. 5.4
    p[np.isnan(p)]=0
    P=np.cumsum(p,2)/np.repmat(np.sum(p,2),(1,m))
    #estimates the ratio r_check to account for the shift from the
    #rayleigh distribution
    Phs=P.T>=2/3
    idx=np.argmax(Phs)
    r_check=r[idx]
    r_check[r_check==0]=np.NaN
    #Shift ratio compared to Rayleigh where Hm0=1.05*Hs.
    r_check=r_check.flatten()/1.05
    m=len(h)
    R=np.sqrt(2)*np.repmat(h.T,(n,1))/np.repmat((hs.*r_check),(1,m))#;%LONGUET-HIGGINS 1983 eq 2.12. Note that R is
    #expressed in term of wave heigth h (rho=h/2 in Longuet-Higgins' paper)
    #slightly non-Rayleigh distribution (as illustrated in fig 2 of LONGUET-HIGGINS 1983)
    F=.5*(erf(R./np.repmat(v,(1,m)))+1)#;%LONGUET-HIGGINS 1983 eq. 5.5 (integrated)
    prob.append(2*R.*np.exp(-R**2).*np.repmat(L,(1,m)).*F)#;%LONGUET-HIGGINS 1983 eq. 5.4

prob=np.array(prob)
prob[np.isnan(prob)]=0;
return prob

def LH_2D(h,tt,HS,SW,TM):
#2D probability density for wave height taking into account spectral width
#see LONGUET-HIGGINS 1983 p.247
#w = waitbar(0,'Estimating Longuet-Higgins joint probability distributions for each time step');
len_hs=len(HS)
while ~np.isempty(HS):
#    %%%%%%%%%%%%%%%%%%%%%to deal with less data and avoid crashing
    ind=min(500,length(HS))
    hs=HS[:ind]
    v=SW[:ind]#;%LONGUET-HIGGINS 1983 abstract SW=sqrt(m0*m2/m1^2-1)
    tm=TM[:ind]
    HS[:ind]=[];
    SW[:ind]=[];
    TM[:ind]=[];
#    %%%%%%%%%%%%%%%%%%%%first estimate the shift in the distribution compared to rayleigh
    L=1/(0.5*(1+(1+v**2)**-0.5))#%LONGUET-HIGGINS 1983 eq. 2.18;
    n=len(L)
    r=np.arange(0,4.01,0.01)
    m=len(r)
    F0=.5*(erf(np.repmat(r,(n,1))/np.repmat(v,(1,m)))+1)#%LONGUET-HIGGINS 1983 eq. 5.5 (integrated)
    p=2*np.repmat(r,(n,1)).*np.exp(-np.repmat(r,(n,1))**2)*np.repmat(L,(1,m))*F0#;%LONGUET-HIGGINS 1983 eq. 5.4
    p[np.isnan(p)]=0
    P=np.cumsum(p,2)/np.repmat(np.sum(p,2),(1,m))
    Phs=P.T>=2/3
    idx=np.argmax(Phs)
    r_check=r[idx]
    r_check[r_check==0]=np.NaN;
    #Shift ratio compared to Rayleigh where Hm0=1.05*Hs.
    r_check=r_check.flatten()/1.05
    o=len(h)
    #%%%%%%%%%%%%%%%%%%adjust the normalized wave amplitude R
    R=np.sqrt(2)*np.repmat(h.flatten().T,(n,1))/np.repmat((hs.*r_check),(1,o))#;%LONGUET-HIGGINS 1983 eq 2.12. Note that R is
    #expressed in term of wave heigth h (rho=h/2 in Longuet-Higgins' paper)
    #slightly non-Rayleigh distribution (as illustrated in fig 2 of LONGUET-HIGGINS 1983)
    oo=len(tt);
    T=repmat(tt,n,1)/np.repmat(tm,1,oo)#;% T=repmat(tt',1,n)./repmat(tm',oo,1);
    v=repmat(v,[1,o,oo]);
    v=np.transpose(v,(1,0,2))
    L=repmat(L,[1 o oo]);
    L=np.transpose(L,(1,0,2))
    R=np.repmat(R,[1 1 oo]);
    R=np.transpose(R,(1,0,2))
    T=repmat(T,[1 1 o]);
    T=np.transpose(T,(2,0,1))
    #%%%%%%%%%%%%%%%%%%%finaly estimate to joint prob distribution: LONGUET-HIGGINS 1983 eq. 2.16 
    if if 'prob' in locals():
        prob=single((2./(pi**.5*v)*(R**2./T**2))*np.exp(-R**2*(1+v**(-2)*(1-T**-1)**2))*L)
    else:
        prob=np.concat(prob,single((2/(pi**.5*v).*(R**2./T**2))*np.exp(-R**2.*(1+v**(-2)*(1-T**-1)**2))*L),1)


prob[np.isnan(prob)]=0
