import numpy as np

def do_wave_pop(time,Hs,Tm,Drr,Tp,Sw,method,dh,Ddir,tbins,exposure,drr_switch,fileout):

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


    if method == 1
        if isempty(SW)
            [pop{1},hbins{1},dbins{1}]=wavepop(Hs,Tm,dt,dh,method);
            [pop{1},hbins{1}]=update_pop(pop{1},hbins{1},length(Hs),dt,exposure);
        else
            [pop{1},hbins{1},dbins{1}]=wavepop(Hs,Tm,dt,dh,method,SW);
            [pop{1},hbins{1}]=update_pop(pop{1},hbins{1},length(Hs),dt,exposure);
        end
    else 
        if method==2
            if isempty(Dir); warndlg('Please make sure you selected the direction time series in the first window','Check direction');return;end
            if length(Ddir)==1
                if Ddir_centered==1
                    Ddir=dir_interval(Ddir,'centred');
                elseif Ddir_centered==0
                    Ddir=dir_interval(Ddir,'not-centred');
                end
            end
        elseif method == 3 || method==4 %replace direction by period
            if method==3 && isempty(Tp); warndlg('Please make sure you selected the Tp time series in the first window','Check Tp');return;end
            if method==4 && isempty(SW); warndlg('Please make sure you selected the spectral width (SW) time series in the first window','Check SW');return;end
            Dir = Tp;
            if length(tbins)>1;Ddir = tbins;else Ddir=0:tbins:25;end
        end
        if isempty(SW)
            
            if drr_switch
                if Ddir_centered
                   [directional_interval]=dir_interval(varargin{2}{3},'centred');
                else
                    [directional_interval]=dir_interval(varargin{2}{3},'not-centred');
                end
                directional_interval=mod(directional_interval,360);
                for j=1:length(directional_interval)
                    if j==length(directional_interval)
                        index=1:length(Hs);
                    else
                        if directional_interval(j+1) <= directional_interval(j)
                            index=(mod(varargin{1}{3,2},360)>directional_interval(j) | mod(varargin{1}{3,2},360)<=directional_interval(j+1));
                        else
                            index=(mod(varargin{1}{3,2},360)>directional_interval(j) & mod(varargin{1}{3,2},360)<=directional_interval(j+1));
                        end
                    end
                    hs=Hs;
                    hs(~index)=NaN;
                    tm=Tm;
                    tm(~index)=NaN;
                    drr=Dir;
                    drr(~index)=NaN;
                    
                    [pop{j},hbins{j},dbins{j}]=wavepop(hs,tm,dt,dh,method,drr,Ddir);
                    [pop{j},hbins{j}]=update_pop(pop{j},hbins{j},length(Hs),dt,exposure);
                end

        
            else
                [pop{1},hbins{1},dbins{1}]=wavepop(Hs,Tm,dt,dh,method,Dir,Ddir);
                [pop{1},hbins{1}]=update_pop(pop{1},hbins{1},length(Hs),dt,exposure);
            end
            
            
        elseif  ~isempty(SW)
            [pop{1},hbins{1},dbins{1}]=wavepop(Hs,Tm,dt,dh,method,Dir,Ddir,SW);%wavepopLH(Hs,Tm,SW,dt,dh,Dir,Ddir)%
            [pop{1},hbins{1}]=update_pop(pop{1},hbins{1},length(Hs),dt,exposure);
        end
    end



    
#  [a1,a2,a3]=fileparts(filename);

# try
#     Pyt = python('python_exist.py');
#     if isequal(deblank(Pyt),'True')
#         Pyt= 1;
#     else
#         Pyt=0;
#     end 
# catch
#     Pyt=0;
# end
# if ~Pyt
#     warning('Install python, numpy and xlsxwriter to write a beautifull excel file')
# end
# if Pyt
#     for T=1:length(pop)
#         clear mat MAT
#         mat{1,1}='';
#         for ii=1:length(dbins{T})-1
#             mat{1,ii+1}=[num2str(dbins{T}(ii)),' to ',num2str(dbins{T}(ii+1))];
#         end
#         mat{1,end+1}='omni';
#         [a,b]=size(pop{T});
#         for ii=1:a
#            if ii~=a
#                 mat{ii+1,1}=['> ',num2str(hbins{T}(ii)),' <= ',num2str(hbins{T}(ii+1))];
#             else
#                 mat{ii+1,1}=['Total'];
#            end
#             mat(ii+1,2:end)=num2cell(pop{T}(ii,:));
#         end


#                 %%
#             %% put into python format
#         MAT='[[';
#         for a=1:size(mat,1)
#             for b=1:size(mat,2)
#                 if ischar(mat{a,b})
#                     MAT=[MAT,'''',mat{a,b},''','];
#                 else
#                     if a==1
#                         MAT=[MAT,'''',num2str(mat{a,b},'%.f'),''','];
#                     else
#                         MAT=[MAT,'''',num2str(mat{a,b},'%.f'),''','];
#                     end
#                 end
#             end
#             MAT(end)=[];
#             MAT=[MAT,'],['];
#         end
#         MAT(end-1:end)=[];
#         MAT=[MAT,']'];
#         if length(pop)==1
#             Sec={'omni'};
#         elseif length(pop)==5;
#             Sec={'N','E','S','W','omni'};
#         elseif length(pop)==9;
#             Sec={'N','NE','E','SE','S','SW','W','NW','omni'};          
#         elseif length(pop)==17;
#             Sec={'N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW','omni'};  
#         end
#         Pyt = python('create_stats_table.py',[a2,'_',sufix,N,'.xlsx'],Sec{T},MAT);
#     end


function [pop,hbins]=update_pop(pop,hbins,len,dt,exposure)

    if ~isempty(exposure)
       pop=pop*exposure/(dt*len/(3600*24*365.25));
    end

    pop=round(pop);
    if size(pop,2)~=1
        pop(:,end+1)=sum(pop,2);
    end

    while all(pop(end,:)==0)
        pop(end,:)=[];
        hbins(end)=[];
    end
    pop(end+1,:)=sum(pop,1);



def wavepop(hs,tm,dt,dh,method,varargin)
'''%wavepop: calculates a population of wave heights in bins of height and
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

%total number of waves for each sample
hs=hs(:);
tm=tm(:);
nw=single(dt./tm);

if nargin>6 && ~isempty(varargin{1})
    dp=varargin{1};dp=dp(:);ddir=varargin{2};
else
    dp=zeros(size(nw));
    if method==4
    ddir=varargin{2};
    else
        ddir=[0 360];
    end
end

if nargin==8 && ~isempty(varargin{3})
    sw=varargin{3};sw=sw(:);type=2;
elseif  nargin==6 && ~isempty(varargin{1})
    sw=varargin{1};sw=sw(:);type=2;
else
    type=1;
end

%construct bin edges for wave height classifiction
if length(dh)==1;
    hbins=0:dh:max(3.0*hs);
else
    hbins=dh;
end

if method == 4
tbins=ddir;
end
%construct bin edges for wave direction
if length(ddir)==1
    dbins=0:360/round(360/ddir):360;
    dbins=mod(dbins-ddir/2,360);%centred in the middle of each bin
else
    dbins=ddir;
end
%assign each sample to a directional bin
for i=1:length(dbins)-1
    if dbins(i) > dbins(i+1)
        inbin{i}=find(dp>=dbins(i) | dp<dbins(i+1));
    else
        inbin{i}=find(dp>=dbins(i) & dp<dbins(i+1));
    end
end

if type==2 && method==4
    cumprob=zeros(length(hbins)-1,size(nw),length(tbins)-1);
else
    cumprob(1,:)=zeros(size(nw));
end
if type==1
    for i=2:length(hbins)
        %cumulative probability wave height is less than upper edeg of bin
        cumprob(i,:)=1-exp(-2*(hbins(i)./hs).^2);
    end
else
    if method==4%2D join-probability distribution
        if length(hs)*length(tbins)*length(hbins)>300000000;warndlg('Please increase bin sizes or time intervals to avoid crashing Matlab','size check');return;
        end
       cumprob=LH_2D(hbins(2:end),tbins(2:end),hs,sw,tm);
    else%1D probability distribution
        cumprob(2:length(hbins),:)=LH(hbins(2:end),hs,sw)';  %note here that cumprob(i,:)
        %represents a time series of probability density for h=hbins(i) (not cumulative prob)
    end
end

if type==2 && method==4
 prob_in_bin=cumprob./repmat(sum(sum(cumprob,1),3),[size(cumprob,1) 1 size(cumprob,3)]);
 prob_in_bin(isnan(prob_in_bin))=0;%just in case we have 0/0 = NaN
 clear cumprob
 nw(isnan(nw))=0;
 %do it for each wave bins instead of full 3d matrix to avoid crashing
 nw=repmat(nw',size(prob_in_bin,3),1);
 pop=zeros(size(prob_in_bin,1),size(prob_in_bin,3));
 w = waitbar(0,'Summing number of waves for each wave bin');
 for i=1:size(prob_in_bin,1)
%  nw=repmat(nw,[1 1 size(prob_in_bin,3)]);
 pop(i,:)=(sum(squeeze(prob_in_bin(i,:,:)).*nw'));
     waitbar(i/size(prob_in_bin,1));
 end
 close(w)
else
    if type==2%this has to be done for type 2 to obtain a normalised cumulative probability
        for k=1:length(hs)
            cumprob(:,k)=cumsum(cumprob(:,k))/sum(cumprob(:,k));
        end
    end
    
    for i=2:length(hbins)
        %subtract previous cumulative probability to get probability in height bin(i)
        prob_in_bin=cumprob(i,:)-cumprob(i-1,:);prob_in_bin=prob_in_bin(:);
        %multiply by number of waves in each sample, sum and assign to the
        %correct directional bin(j)
        for j=2:length(dbins)
            pop(i-1,j-1)=nansum(prob_in_bin(inbin{j-1}).*nw(inbin{j-1}));
        end
    end
end

function prob=LH(h,HS,SW)
%1D probability density for wave height taking into account spectral width
%see LONGUET-HIGGINS 1983 p.247
prob=[];
while ~isempty(HS)
    ind=min(5000,length(HS));%to deal with less data and avoid crashing
    hs=HS(1:ind);
    v=SW(1:ind);%LONGUET-HIGGINS 1983 abstract SW=sqrt(m0*m2/m1^2-1)
    HS(1:ind)=[];
    SW(1:ind)=[];
    
    %first estimate the shift in the distribution compared to rayleigh
    L=1./(0.5*(1+(1+v.^2).^-0.5));%LONGUET-HIGGINS 1983 eq. 2.18;
    n=length(L);
    r=0:.01:4;
    m=length(r);
    F0=.5*(erf(repmat(r,n,1)./repmat(v,1,m))+1);%LONGUET-HIGGINS 1983 eq. 5.5 (integrated)
    p=2*repmat(r,n,1).*exp(-repmat(r,n,1).^2).*repmat(L,1,m).*F0;%LONGUET-HIGGINS 1983 eq. 5.4
    p(isnan(p))=0;
    P=cumsum(p,2)./repmat(sum(p,2),1,m);
    %estimates the ratio r_check to account for the shift from the
    %rayleigh distribution
    Phs=P'>=2/3;
    [~,idx]=max(Phs);
    r_check=r(idx);
    r_check(r_check==0)=NaN;
    %Shift ratio compared to Rayleigh where Hm0=1.05*Hs.
    r_check=r_check(:)/1.05;
    m=length(h);
    R=sqrt(2)*repmat(h(:)',n,1)./repmat((hs.*r_check),1,m);%LONGUET-HIGGINS 1983 eq 2.12. Note that R is
    %expressed in term of wave heigth h (rho=h/2 in Longuet-Higgins' paper)
    %slightly non-Rayleigh distribution (as illustrated in fig 2 of LONGUET-HIGGINS 1983)
    F=.5*(erf(R./repmat(v,1,m))+1);%LONGUET-HIGGINS 1983 eq. 5.5 (integrated)
    prob=[prob; 2*R.*exp(-R.^2).*repmat(L,1,m).*F];%LONGUET-HIGGINS 1983 eq. 5.4
end
prob(isnan(prob))=0;

function prob=LH_2D(h,tt,HS,SW,TM)
%2D probability density for wave height taking into account spectral width
%see LONGUET-HIGGINS 1983 p.247
w = waitbar(0,'Estimating Longuet-Higgins joint probability distributions for each time step');
len=length(HS);
while ~isempty(HS)
    %%%%%%%%%%%%%%%%%%%%%to deal with less data and avoid crashing
    ind=min(500,length(HS));
    hs=HS(1:ind);
    v=SW(1:ind);%LONGUET-HIGGINS 1983 abstract SW=sqrt(m0*m2/m1^2-1)
    tm=TM(1:ind);
    HS(1:ind)=[];
    SW(1:ind)=[];
    TM(1:ind)=[];
    %%%%%%%%%%%%%%%%%%%%first estimate the shift in the distribution compared to rayleigh
    L=1./(0.5*(1+(1+v.^2).^-0.5));%LONGUET-HIGGINS 1983 eq. 2.18;
    n=length(L);
    r=0:.01:4;
    m=length(r);
    F0=.5*(erf(repmat(r,n,1)./repmat(v,1,m))+1);%LONGUET-HIGGINS 1983 eq. 5.5 (integrated)
    p=2*repmat(r,n,1).*exp(-repmat(r,n,1).^2).*repmat(L,1,m).*F0;%LONGUET-HIGGINS 1983 eq. 5.4
    p(isnan(p))=0;
    P=cumsum(p,2)./repmat(sum(p,2),1,m);
    Phs=P'>=2/3;
    [~,idx]=max(Phs);
    r_check=r(idx);
    r_check(r_check==0)=NaN;
    %Shift ratio compared to Rayleigh where Hm0=1.05*Hs.
    r_check=r_check(:)/1.05;
    o=length(h);
    %%%%%%%%%%%%%%%%%%adjust the normalized wave amplitude R
    R=sqrt(2)*repmat(h(:)',n,1)./repmat((hs.*r_check),1,o);%LONGUET-HIGGINS 1983 eq 2.12. Note that R is
    %expressed in term of wave heigth h (rho=h/2 in Longuet-Higgins' paper)
    %slightly non-Rayleigh distribution (as illustrated in fig 2 of LONGUET-HIGGINS 1983)
    oo=length(tt);
    T=repmat(tt,n,1)./repmat(tm,1,oo);% T=repmat(tt',1,n)./repmat(tm',oo,1);
    v=repmat(v,[1 o oo]);
    v=permute(v,[2 1 3]);
    L=repmat(L,[1 o oo]);
    L=permute(L,[2 1 3]);
    R=repmat(R,[1 1 oo]);
    R=permute(R,[2 1 3]);
    T=repmat(T,[1 1 o]);
    T=permute(T,[3 1 2]);
    %%%%%%%%%%%%%%%%%%%finaly estimate to joint prob distribution: LONGUET-HIGGINS 1983 eq. 2.16 
    if ~exist('prob','var')
        prob=single((2./(pi^.5.*v).*(R.^2./T.^2)).*exp(-R.^2.*(1+v.^(-2).*(1-T.^-1).^2)).*L);
    else
        prob=cat(2,prob,single((2./(pi^.5.*v).*(R.^2./T.^2)).*exp(-R.^2.*(1+v.^(-2).*(1-T.^-1).^2)).*L));
    end
     waitbar(1-length(HS)/len);
end
prob(isnan(prob))=0;
close(w)