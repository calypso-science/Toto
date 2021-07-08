""" This subroutine excludes spike noise from Acoustic Doppler 
Velocimetry (ADV) data using phase-space method, using 
modified Goring and Nikora (2002) method by Nobuhito Mori (2005).
Further modified by Joseph Ulanowski to remove offset in output (2014). 
"""
import numpy as np
def despike_phasespace3d( input_array,args={}) :
    # --- initial setup
    # number of maximum iternation
    f=input_array.to_numpy(copy=True)
    n_iter = 20
    n_out  = 999

    n      = f.shape[0]

    f_mean = 0#     % do not calculate f_mean here, as it will be affected by spikes (was: f_mean = nanmean(fi);)

    lamba = np.sqrt(2*np.log(n));



    # --- loop
    n_loop = 1;

    while (n_out!=0) & (n_loop <= n_iter):
        # step 0
        f_mean=f_mean+np.nanmean(f) # accumulate offset value at each step [J.U.]
        f = f - np.nanmean(f)

        # step 1: first and second derivatives
        f_t  = np.gradient(f,axis=0)
        f_tt = np.gradient(f_t,axis=0)

        # step 2: estimate angle between f and f_tt axis
        if n_loop==1:
          theta = np.arctan2( np.nansum(f*f_tt), np.nansum(f**2) )
        

        #step 3: checking outlier in the 3D phase space
        xp,yp,zp,ip,coef = func_excludeoutlier_ellipsoid3d(f,f_t,f_tt,theta)


        # --- excluding data

        n_nan_1 = np.nonzero(np.isnan(f))[0].shape[0]
        f[ip]  = np.nan
        n_nan_2 = np.nonzero(np.isnan(f))[0].shape[0]
        n_out   = n_nan_2 - n_nan_1;

        # --- end of loop
        
        n_loop += 1



    # --- post process
    go = f + f_mean;    # add offset back
    input_array.values[:]=go
    return input_array

def func_excludeoutlier_ellipsoid3d(xi,yi,zi,theta):
    """    %
        % This program excludes the points outside of ellipsoid in two-
        % dimensional domain
    """

    n = np.max(xi.shape)
    lamba = np.sqrt(2*np.log(n))

    xp = [];
    yp = [];
    zp = [];
    ip = [];
    # --- rotate data

    if theta == 0:
      X = xi
      Y = yi
      Z = zi
    else:
        R = np.array([ [np.cos(theta), 0,  np.sin(theta)],[ 0, 1, 0],[ -np.sin(theta), 0, np.cos(theta)]])
        X = xi*R[0,0] + yi*R[0,1] + zi*R[0,2]
        Y = xi*R[1,0] + yi*R[1,1] + zi*R[1,2]
        Z = xi*R[2,0] + yi*R[2,1] + zi*R[2,2]
    


    # --- preprocess
    

    a = lamba*np.nanstd(X)
    b = lamba*np.nanstd(Y)
    c = lamba*np.nanstd(Z)

    # --- main
    
    m = -1
    for i in range(0,n):
      x1 = X[i]
      y1 = Y[i]
      z1 = Z[i]
      # point on the ellipsoid
      x2 = a*b*c*x1/np.sqrt((a*c*y1)**2+b**2*(c**2*x1**2+a**2*z1**2))
      y2 = a*b*c*y1/np.sqrt((a*c*y1)**2+b**2*(c**2*x1**2+a**2*z1**2))
      zt = c**2* ( 1 - (x2/a)**2 - (y2/b)**2 )
      if z1 < 0:
        z2 = -np.sqrt(zt)
      elif z1 > 0:
        z2 = np.sqrt(zt)
      else:
        z2 = 0
      

      # check outlier from ellipsoid
      dis = (x2**2+y2**2+z2**2) - (x1**2+y1**2+z1**2)
      if dis < 0 :
        m = m + 1
        ip.append( i)
        xp.append(xi[i])
        yp.append(yi[i])
        zp.append(zi[i])

    coef=np.ndarray((3,))
    coef[0] = a
    coef[1] = b
    coef[2] = c


    return  xp,yp,zp,ip,coef


if __name__ == '__main__':
    import pandas as pd
    import matplotlib.pyplot as plt
    
    
    x = np.arange(0,10*np.pi,0.1)
    y=  np.sin(x)
    y[99]=100
    y[150]=-44

    df = pd.DataFrame(y, columns=list('e'))
    plt.plot(df['e'],'b')
    go=func_despike_phasespace3d(df)
    
    plt.plot(go['e'],'r')
    plt.show()