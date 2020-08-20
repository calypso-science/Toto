import pandas as pd
import numpy as np
import xarray as xr
from ...core.toolbox import wavenuma

@pd.api.extensions.register_dataframe_accessor("DataTransformation")
class DataTransformation:
    def __init__(self, pandas_obj):
#        self._validate(pandas_obj)
        self.data = pandas_obj
        self.dfout = pd.DataFrame(index=self.data.index.copy())

    def wind_profile(self,ws='ws',opts={
        'Level of input wind speed (in meters)':10.,\
        'Averaging period of input wind speed (in minutes)':10.,\
        'Output level (in meters)':10.,\
        'Output time averaging (in minutes)':10.}):
        """%The function computes wind at user-input level and time averaging period
        %based on an input wind field.
        % based on the NPD spectrum 
        % biblio : PDF file in 
        %JIRA ENTRY : Include the updated API wind profile / gust equations into GIMP2 
        % https://jira.metocean.co.nz/browse/MLB-7"""

        opt={   'Level of input wind speed (in meters)':10.,\
                'Averaging period of input wind speed (in minutes)':10.,\
                'Output level (in meters)':10.,\
                'Output time averaging (in minutes)':10.}

        opt.update(opts)

        U_inp=self.data[ws]
        level_inp=opt['Level of input wind speed (in meters)'];
        level_out=opt['Output level (in meters)']
        t_av_in=opt['Averaging period of input wind speed (in minutes)']*60. #into seconds
        t_av_out=opt['Output time averaging (in minutes)']*60.

        #first work out the the wind speed at 10 m above ground 
        if ~((level_inp>=9.) & (level_inp<=11.)):
            U10=U_inp*((10./level_inp)**0.143) #maybe use 0.11 if ocean ..
    
        else:
            U10=U_inp.copy()
        
        #then work out 60 min avergaed if its not the one input
        if ~((t_av_in>=59.*60.) & (t_av_in<=61.*60.)):
            a=-0.41*0.06*np.log(t_av_in/3600)*0.0131*3.2808
            b=1-0.41*0.06*np.log(t_av_in/3600)
            c=-U10
            U10T3600=(-b+((b**2)-4*a*c)**0.5)/(2*a) #1 hour mean wind speed at 10 m above ground
        
        else:
            U10T3600=U10.copy()
        

        #Now apply the equation to output wind at any given level and any given average
        #time from the hourly avergaed at 10 m
        C=0.0573*np.sqrt( 1 + 0.15*U10T3600)
        Iz=0.06*(1+0.043*U10T3600)*((level_out/10)**-0.22)
        Uz=U10T3600*(1+C*np.log(level_out/10))
        Uz=Uz*(1-0.41*Iz*np.log(t_av_out/3600))
        self.dfout['Uz']=Uz
        return self.dfout

    def dav_to_layers(self,u='u',dp='dp',args={'z':0.,'z0':0.001}):
        opt={'z':0.,'z0':0.001}
        opt.update(args)      

        U=self.data[u]
        h=np.nanmean(self.data[dp])
        z0=opt['z0']
        Z=np.abs(opt['z']);
        z=h-Z;
        
        if z==0:
            z=0.0001
        
        fac=(np.log(z/z0)/(np.log(h/z0)-1))
        self.dfout[self.data[u].short_name+'_lev_'+str(Z)]=U*fac
        return self.dfout


    def layers_to_dav(self,u='u',dp='dp',args={'z':0.,'z0':0.001}):
        opt={'z':0.,'z0':0.001}
        opt.update(args)

        U=self.data[u]
        h=np.nanmean(self.data[dp])
        z0=opt['z0']
        Z=np.abs(opt['z']);
        z=h-Z;
        if z==0:
            z=0.0001     


        fac=((np.log(h/z0)-1)/np.log(z/z0))
        self.dfout[self.data[u].short_name+'m']=U*fac
        return self.dfout

    def hs_sea(self,hs='hs',hs_swell='hs_swell'):
        self.dfout['Hs_sea']=np.sqrt(self.data[hs]**2-self.data[hs_swell]**2)
        return self.dfout



    def Oribital_velocity(self,dp='dp',tp='tp',hs='hs',args={'z':0.}):
        z=args['z']
        Z=np.abs(z)

        z=self.data[dp]-Z;
        pi2=2*np.pi
        k=wavenuma(pi2/self.data[tp],self.data[dp])
        Uorb=pi2*(self.data[hs]/2)/self.data[tp]*np.cosh(k*z)/np.sinh(k*self.data[dp])
        self.dfout['Uorb']=Uorb
        return self.dfout

    def uv_to_spddir(self,u='u', v='v', args={'Origin':{'going to':True,'coming from':False}}):
        """Converts (u, v) to (spd, dir).
        Args:
            u (array): eastward wind component
            v (array): northward wind component
            coming_from (bool): True for output directions in coming-from convention, False for going-to
        Returns:
            mag (array): magnitudes
            direc (array): directions (degree)
        """

        u=self.data[u]
        v=self.data[v]
        ang_rot = 180 if args['Origin']=='coming from' else 0
        vetor = u + v * 1j
        mag = np.abs(vetor)
        direc = xr.ufuncs.angle(vetor, deg=True) + ang_rot
        direc = np.mod(90 - direc, 360)
        self.dfout['spd']=mag
        self.dfout['drr']=direc

        return self.dfout



    def spddir_to_uv(self,spd='spd', direc='direc', args={'Origin':{'going to':True,'coming from':False}}):
        """Converts (spd, dir) to (u, v).
        Args:
            spd (array): magnitudes to convert
            direc (array): directions to convert (degree)
            coming_from (bool): True if directions in coming-from convention, False if in going-to
        Returns:
            u (array): eastward wind component
            v (array): northward wind component
        """

        spd=self.data[spd]
        direc=self.data[direc]
        ang_rot = 180 if args['Origin']=='coming from' else 0
        direcR = np.deg2rad(direc + ang_rot)
        u = spd * np.sin(direcR)
        v = spd * np.cos(direcR)
        self.dfout['u']=u
        self.dfout['v']=v
        return self.dfout