import numpy as np
from scipy.interpolate import interp1d


def do_ssh_to_wave(time,mag,unit,nperseg,noverlap,nfft,detrend,period,plotfreq,fileout,display):

    sint=(time[2]-time[1]).seconds
    Tmin=period[0]
    Tmax=period[1]
    if period[0] <= 1.9999*sint:
        return print('The minimum analysed period must be at least twice the sampling period (i.e. >= '+str(2*sint)+' s)')


    if period[1] > nfft*sint:
        return print('The minimum window and nfft length must be larger than the maximum plotting period (i.e. window >= '+str(np.round(Tmax/sint))+' and nfft > '+str(np.round(Tmax/sint))+')')

    bad=np.isnan(mag)
    mag=mag[~bad] #removes possible NaN on the edges of the time series


    #convert window and overlap in number of time steps
    overlap_H=noverlap/3600
    window = int(nperseg/sint)
    overlap = int(noverlap/sint)


    #start at the first fix hour
    HH=time.hour
    MM=time.minute

    #make sure we start the time series at the right time in order to have
    #windows centred on the hour,30min,15min etc...
    start=0
    # if overlap_H>=1
    #     start=find(ismember(HH,0:overlap_H:23), 1 )-round(window/2);
    # else:
    #     overlap_M=overlap_H*60;%convert to min
    #     start=find(ismember(MM,0:overlap_M:59), 1 )-round(window/2);

    # if start<=0
    #     m=0;
    #     while start <=0
    #         if overlap_H>=1
    #             ind_change=find(diff(HH)~=0,1);
    #             start=m+find(ismember(HH,0:overlap_H:23), 1 )-round(window/2);
    #             HH(1:ind_change)=[];
    #         else
    #             ind_change=find(diff(MM)~=0,1);
    #             start=m+find(ismember(MM,0:overlap_M:59), 1 )-round(window/2);
    #             MM(1:ind_change)=[];
    #         end
    #         m=m+ind_change;
    #     end
    # end

    mag=mag[start:]
    time=time[start:]

    hs=np.empty((np.ceil((len(mag)-window)/overlap),6)) # HS,Hmax,H10,ts,t10,tmax

for i in range(0,length(mag)-window,overlap):
    data =mag[i:i+window]
    N=len(data);
    t=time[i:i+window]
    #%%%%%%%%%%%%%identify the length of NaN blocks
    a=np.all(np.isnan(data),1).astype(int)
    nan_block_length=[sum(1 for i in g) for k,g in groupby(a) if k==1]

    #%%%%%%%%%%%%%%%%%do spectrum analysis
    if  len(a[a==1]) < N/2 & len((nan_block_length>Tmin/sint).nonzero()[0]) < 4: 
            set_interp = interp1d(t[~np.isnan(data)], data[~np.isnan(data)])
            data=set_interp(t) #removes NaN
            data=data[~np.isnan(data)] #removes possible NaN on the edges of the time series
        
            freqs, psd = signal.welch(mag,fs=1./sint,nperseg=int(nperseg/sint),noverlap=int(noverlap/sint),nfft=int(nfft/sint),detrend=detrend)
            gd=freqs>=Tmin & freqs<=Tmax 
            WB=specstats(freqs[gd],psd[gd],WB,1/8);
            T=time[i+int(window/2)]
      
    else:
        T=time[i+int(window/2)]
        WB=np.Nan#matrix=[matrix;T,ones(1,size(matrix,2)-1)*NaN];
    



# dataset{1,1}=[matrix(:,1) matrix(:,2) ones(size(matrix,1),1)]; dataset{1,2}='Hs';dataset{1,2}='Hs [m]';
# dataset{2,1}=[matrix(:,1) matrix(:,3) ones(size(matrix,1),1)]; dataset{2,2}='Tp';dataset{2,2}='Tp [s]';
# dataset{3,1}=[matrix(:,1) matrix(:,4) ones(size(matrix,1),1)]; dataset{3,2}='Tm01';dataset{3,2}='Tm01 [s]';
# dataset{4,1}=[matrix(:,1) matrix(:,5) ones(size(matrix,1),1)]; dataset{4,2}='Tm02';dataset{4,2}='Tm02 [s]';

# dataset{5,1}=[matrix(:,1) matrix(:,6) ones(size(matrix,1),1)]; dataset{5,2}='Hs_sw';dataset{5,2}='Hs_sw [m]';
# dataset{6,1}=[matrix(:,1) matrix(:,7) ones(size(matrix,1),1)]; dataset{6,2}='Tp_sw';dataset{6,2}='Tp_sw [s]';
# dataset{7,1}=[matrix(:,1) matrix(:,8) ones(size(matrix,1),1)]; dataset{7,2}='Tm01_sw';dataset{7,2}='Tm01_sw [s]';
# dataset{8,1}=[matrix(:,1) matrix(:,9) ones(size(matrix,1),1)]; dataset{8,2}='Tm02_sw';dataset{8,2}='Tm02_sw [s]';

# dataset{9,1}=[matrix(:,1) matrix(:,10) ones(size(matrix,1),1)]; dataset{9,2}='Hs_sea';dataset{9,2}='Hs_sea [m]';
# dataset{10,1}=[matrix(:,1) matrix(:,11) ones(size(matrix,1),1)]; dataset{10,2}='Tp_sea';dataset{10,2}='Tp_sea [s]';
# dataset{11,1}=[matrix(:,1) matrix(:,12) ones(size(matrix,1),1)]; dataset{11,2}='Tm01_sea';dataset{11,2}='Tm01_sea [s]';
# dataset{12,1}=[matrix(:,1) matrix(:,13) ones(size(matrix,1),1)]; dataset{12,2}='Tm02_sea';dataset{12,2}='Tm02_sea [s]';

