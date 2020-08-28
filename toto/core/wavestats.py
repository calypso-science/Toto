import numpy as np
def split(S,freq, fmin=None, fmax=None):
        """Split spectra over freq and/or dir dims.
        Args:
            - fmin (float): lowest frequency to split spectra, by default the lowest.
            - fmax (float): highest frequency to split spectra, by default the highest.
            - dmin (float): lowest direction to split spectra over, by default min(dir).
            - dmax (float): highest direction to split spectra over, by default max(dir).
        Note:
            - spectra are interpolated at `fmin` / `fmax` if they are not present in self.freq
        """
        assert fmax > fmin if fmax and fmin else True, "fmax needs to be greater than fmin"

        # Slice frequencies
        if fmax is None:
            fmax=np.inf 

        if fmin is None:
            fmin=-np.inf

        gd_freq=(freq>=fmin) & (freq<=fmax)
        other_spec = S[gd_freq]
        other_freq = freq[gd_freq]

        # Interpolate at fmin
        if (fmin is not None) and (other_freq.min() > fmin) and (freq.min() <= fmin):
            fint,sint=_interp_freq(freq,S,fmin)
            other_spec = np.concatenate((sint, other_spec))
            other_freq = np.concatenate((fint, other_freq))

        # Interpolate at fmax
        if (fmax is not None) and (other_freq.max() < fmax) and (freq.max() >= fmax):
            fint,sint=_interp_freq(freq,S,fmax)
            other_spec = np.concatenate((other_spec, sint))
            other_freq = np.concatenate((other_freq, fint))

        return other_spec,other_freq


def _interp_freq(freq,S, fint):
    """Linearly interpolate spectra at frequency fint.
    Assumes self.freq.min() < fint < self.freq.max()
    Returns:
        DataArray with one value in frequency dimension (relative to fint)
        otherwise same dimensions as self._obj
    """
    assert (
        freq.min() < fint < freq.max()
    ), "Spectra must have frequencies smaller and greater than fint"
    ifreq = freq.searchsorted(fint)
    #import pdb;pdb.set_trace()
    df = np.diff(freq[ifreq - 1: ifreq+1])

    Sint = S[ifreq] * (
        fint - freq[ifreq - 1]
    ) + freq[ifreq - 1] * (
        freq[ifreq] - fint
    )
    sint=Sint / df

    return [fint],sint


def specstats(sp,freq,fmin=1/25.,fmax=1/3.,cutoff=1/8.):
    #-----------------------------------------------------------
    #%  Based on code written by Richard Gorman, VIMS, University of Waikato
    #%
    #%  Make the spectrum a column vector.
    #%

    #
    #  Find the peak frequency and spectral density.
    #
    sp,freq=split(sp,freq, fmin=fmin,fmax=fmax)

    stats={}
    stats['tot']=get_stats(sp,freq)

    S_sw,freq_sw=split(sp,freq, fmax=cutoff)
    stats['sw']=get_stats(S_sw,freq_sw)
    
    S_sea,freq_sea=split(sp,freq, fmin=cutoff)
    stats['sea']=get_stats(S_sea,freq_sea)

    return stats

def get_stats(sp,freq):
    stat={}
    Xmom=np.empty((5,))

    smax= np.max(sp)
    imax = np.argmax(sp);

    ifit=[imax-1, imax, imax+1];
    ifit=[max(min(x, len(sp)-1), 0) for x in ifit]


    p=np.polyfit(freq[ifit],sp[ifit],2);
    stat['fmax'] = -0.5*p[1]/p[0]
    stat['smax']= sp[imax]

    tmp=0.5*np.ones((len(freq),1))
    tmp[0]=1
    tmp[-1]=1
    tmp2=np.concatenate((np.array([0]),np.diff(freq)))+np.concatenate((np.diff(freq),np.array([0])))

    delf=tmp[:,0]*tmp2 # works even if frequencies are not evenly distributed
    # delf=freq(2)-freq(1);

    #  0th and 1st moments:

    Xmom[0] = np.sum(sp*delf);# - .5*sp(1)*delf(1); % 0-th moment
    temp = sp*delf*freq
    Xmom[1] = np.sum(temp)# % 1st moment

    #  Goda's spectral peakedness parameter:

    QP = np.sum(temp*sp)
    #
    #  2nd, 3rd and 4th moments:
    #
    for j in range(2,5):
      temp = temp*freq
      Xmom[j] = np.sum(temp)

    stat['Xmom0']=Xmom[0]
    stat['Xmom1']=Xmom[1]
    stat['Xmom2']=Xmom[2]
    stat['Xmom3']=Xmom[3]
    stat['Xmom4']=Xmom[4]
    stat['Hs'] =  4*np.sqrt(np.abs(Xmom[0]))
    stat['Tm01'] = Xmom[0]/Xmom[1]
    stat['Tm02'] =  np.sqrt(np.abs(Xmom[0]/Xmom[2]))
    stat['Fmn'] = Xmom[1]/Xmom[0]
    stat['Tcr'] =  np.sqrt(np.abs(Xmom[2]/Xmom[4]))
    stat['T2'] = stat['Tm01']*stat['fmax']
    stat['QP']=QP/(Xmom[0]**2) #Goda (1970, Eq. 44)(Tech. note Port and Harbour res.)
    stat['SWe'] = np.sqrt(1 - Xmom[2]**2/(Xmom[0]*Xmom[4])) #%Cartwright and Longuet-Higgins (1956, Eq. 1.20) (Proc. R. Soc. London A)
    stat['SW'] = np.sqrt(Xmom[0]*Xmom[2]/Xmom[1]**2-1) #%Longuet-Higgins (1984, Eq. 1.1) (Phil. Trans. R. Soc. London. A)

    return stat



if __name__ == "__main__":
    S=np.random.rand(15,)
    freq=np.arange(1/25.,1/3.,0.02)

    stat=specstats(S,freq,1/8)
    print(stat)


