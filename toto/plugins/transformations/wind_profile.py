import pandas as pd
import numpy as np
import xarray as xr
from ...core.toolbox import wavenuma,uv2spdir,spdir2uv,qkhfs

@pd.api.extensions.register_dataframe_accessor("DataTransformation")
class DataTransformation:
    def __init__(self, pandas_obj):
#        self._validate(pandas_obj)
        self.data = pandas_obj
        self.dfout = pd.DataFrame(index=self.data.index.copy())

    def rotation(self,wd='wd',args={'rotate by': 180}):
        """ this function will rotate direction
        usefull for changing wind coming from to going to"""
        ang=args['rotate by']
        u=self.data[wd]
        self.dfout[wd+'_%.f' % ang]=np.mod(u+ang,360)
        return self.dfout

    def wind_profile(self,ws='ws',args={
        'Level of input wind speed (in meters)':10.,\
        'Averaging period of input wind speed (in minutes)':10.,\
        'Output level (in meters)':10.,\
        'Output time averaging (in minutes)':10.}):
        """ The function computes wind at user-input level and time averaging period
            based on an input wind field.
            based on the NPD spectrum 
        """

        opt={   'Level of input wind speed (in meters)':10.,\
                'Averaging period of input wind speed (in minutes)':10.,\
                'Output level (in meters)':10.,\
                'Output time averaging (in minutes)':10.}

        opt.update(args)

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
        """ Change depth-average value to any depth"""

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
        self.dfout[u+'_lev_'+str(Z)]=U*fac
        return self.dfout


    def layers_to_dav(self,u='u',dp='dp',args={'z':0.,'z0':0.001}):
        """Change from velocity at a specify l;ayer to depth-average value"""

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
        self.dfout[u+'m']=U*fac
        return self.dfout

    def hs_sea(self,hs='hs',hs_swell='hs_swell',args={}):
        """Calculate Hs Sea from Hs swell and Hs Total"""

        self.dfout['Hs_sea']=np.sqrt(np.abs(self.data[hs]**2-self.data[hs_swell]**2))
        return self.dfout



    def Oribital_velocity(self,dp='dp',tp='tp',hs='hs',args={'z':0.}):
        """Calculate the orbital velocity"""
        
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

        mag,direc=uv2spdir(self.data[u],self.data[v],args['Origin'])

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
        u,v=spdir2uv(self.data[spd],self.data[direc],args['Origin'])

        self.dfout['u']=u
        self.dfout['v']=v
        return self.dfout


    def bed_shear_stress(self,spd='spd',drr='drr',hs='hs',dpm='dpm',tp='tp',water_depth='depth',
                        args={'water_depth':10,
                        'mode':{'dav':'On','3D':'Off'},
                        'rho_water':1027,
                              'z0': 0.001,
                        'inlude_current': {'On','Off'},
                        'inlude_wave': {'On','Off'},
                        'wave_friction': {'Swart':'On','Soulsby':'Off'}
                        }):
        """
        Computation of bed shear stress due to current and waves
        current-related stress is computed following a drag-coefficient approach
        wave-related stress is computed following Van Rijn approach
        Combined wave-current mean and max stresses are computed following Soulsby(1995) approach
        https://odnature.naturalsciences.be/coherens/manual#manual
        https://odnature.naturalsciences.be/downloads/coherens/documentation/chapter7.pdf#nameddest=Bed_shear_stresses
        
        http://www.coastalwiki.org/wiki/Shallow-water_wave_theory#
        http://www.coastalwiki.org/wiki/Shallow-water_wave_theory#Seabed_Friction  
        General relationships obtained from :
        https://repository.tudelft.nl/islandora/object/uuid%3Aea12eb20-aee3-4f58-99fb-ebc216e98879
        Description of TRANSPOR2004 and Implementation in Delft3D-ONLINE
        Take from the work of Simon Wepp in Opendrift


        Parameters
        ~~~~~~~~~~

        spd : str
            Name of the column from which to get current speed.
        drr: str, optional
            Column name representing the current direction.  
        hs : str, optional
            Column name representing the wave height.
        tp : str, optional
            Column name representing the wave period.
        dpm: str, optional
            Column name representing the wave direction.        
        water_depth: str, optional
            Column name representing the water depth.

        args: dict
            Dictionnary with the folowing keys:
            water_depth: float
                Total water depth or level from which the current was taken
            mode: str
                Use `3D` or `dav` for 3D current or depth=average current. default `dav`
            rho_water float:
                Sea water density kg/m3, default 1027
            z0 float:
                Roughness height, default 0.001
            inlude_current str:
                `On` or `Off` if calculating the shear stress from current speed
            inlude_wave str:
                `On` or `Off` if calculating the shear stress from wave
            wave_friction str:
                `Soulsby` or `Swart` formulae, default `Swart`

        Examples:
        ~~~~~~~~~
        >>> df=tf['test1']['dataframe'].DataTransformation.bed_shear_stress(spd='spd',hs='hs',tp='tp',args={'water_depth':10})
        >>> 
        """
        if args.get('mode','dav'):
            dav=True
        else:
            dav=False
        wave_friction='swart'
        if args.get('wave_friction','swart').lower()=='soulsby':
            wave_friction='soulsby'

        include_current=True
        include_wave=True
        if args.get('include_current','On')=='Off':
            include_current=False
        if args.get('include_wave','On')=='Off':
            include_wave=False


        rho_water = args.get('rho_water',1027) # kg/m3
        z0 = args.get('z0',0.001) # roughness height
        if water_depth in self.data:
            water_depth = np.abs(self.data[water_depth])
        else:
            water_depth = np.abs(args.get('water_depth',10)) # water depth positive down
        



        
        if include_current:
            #######################################################
            # current-related bed shear stress
            #######################################################
            current_speed = self.data[spd] # depth-averaged current 
            if dav:
                # depth-averaged current approach :
                Cdrag=( 0.4 /(np.log(abs(water_depth/z0))-1) )**2
                #Now compute the bed shear stress [N/m2] 
                tau_cur=rho_water*Cdrag*current_speed**2 # eq. 7.1 in COHERENS Manual
            else:
                #3D currents:
                Cdrag=(0.4/np.log(water_depth/z0))**2
                tau_cur=rho_water*Cdrag*current_speed**2 # eq. 7.1 in COHERENS Manual
        else:
            tau_cur=0
            print('No shear stress from currents')


        if include_wave:
            #######################################################
            # wave-related bed shear stress (if wave available)
            #######################################################
            hs = self.data[hs]
            tp = self.data[tp]

            # wave-related roughness

            # see VanRijn 
            # https://tinyurl.com/nyjcss5w
            # SIMPLE GENERAL FORMULAE FOR SAND TRANSPORT IN RIVERS, ESTUARIES AND COASTAL WATERS
            # >> page 6
            # 
            # Note : VanRijn 2007 suggests same equations than for current-related roughness 
            # where 20*d50 <ksw<150*d50: Here we are using Nikuradse roughness for consistency 
            # with the use of z0 in the current-related shear stress 

            ksw=30*z0 # wave related bed roughness - taken as Nikuradse roughness 
            w=2*np.pi/tp # angular frequency
            kh = qkhfs( w, water_depth ) # from dispersion relationship 
            Adelta = hs/(2*np.sinh(kh)) # peak wave orbital excursion 
            Udelta = (np.pi*hs)/(tp*np.sinh(kh))  # peak wave orbital velocity linear theory 
            # wave-related friction coefficient (Swart,1974) and eq. 3.8 on VanRijn pdf
            # see also COHERENS manual eq. 7.17 which is equivalent since exp(a+b) =exp(a)*exp(b)

            if wave_friction=='soulsby':
                fw = 0.237 * (Adelta/ksw)**-0.52 #eq. 7.18 COHERENS, not used for now
            else:
                fw = np.exp(-5.977+5.213*(Adelta/ksw)**-0.194)  
                fw = np.minimum(fw,0.3)
            tau_wave = 0.25 * rho_water * fw * (Udelta)**2 # wave-related bed shear stress eq. 3.7 on VanRijn pdf

        else:
            tau_wave=0

        if include_wave & include_current:
            #cycle mean bed shear stress according to Soulsby,1995, see also COHERENS manual eq. 7.14
            tau_cw=tau_cur*(1+1.2*(tau_wave/(tau_cur+tau_wave))**3.2)
            # max bed shear stress during wave cycle >> used for the resuspension criterion.
            
            if drr in self.data and dpm in self.data:
                print('calculating angle difference')
                dpm=np.mod(self.data[dpm]+0,360)*np.pi/180
                drr=self.data[drr]*np.pi/180
                theta_cur_dir=np.arctan2(np.sin(drr-dpm), np.cos(drr-dpm))
                print(theta_cur_dir.max())
                print(theta_cur_dir.min())
            else:
                theta_cur_dir = 0.0 #angle between direction of travel of wave and current, in radians, in practice rarely known so assume 0.0 for now
                print('angle between direction of travel of wave and current not calculated')

            tau_cw_max = ( tau_cur**2 + tau_wave**2 + 2*tau_cur*tau_wave*np.cos(theta_cur_dir) )**0.5 # COHERENS eq. 7.15
        else:
            if include_wave:
                tau_cw=tau_cw_max=tau_wave
            elif include_current:
                tau_cw=tau_cw_max=tau_cur

        self.dfout['tau_cw']=tau_cw
        self.dfout['tau_cw_max']=tau_cw_max

        return self.dfout


    
