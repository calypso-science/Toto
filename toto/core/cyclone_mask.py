
import os
import urllib.request
import xarray as xr
import numpy as np
from datetime import datetime,time
from ..core.toolbox import sph2cart
from matplotlib.dates import date2num
import sys

YEAR0=1950

def binaries_directory():
    """Return the installation directory, or None"""


    if '--user' in sys.argv:
        import site
        paths = (site.getusersitepackages(),)
    else:
        py_version = '%s.%s' % (sys.version_info[0], sys.version_info[1])
        paths = (s % (py_version) for s in (

            sys.prefix + '/lib/python%s/dist-packages/',
            sys.prefix + '/lib/python%s/site-packages/',
            sys.prefix + '/local/lib/python%s/dist-packages/',
            sys.prefix + '/local/lib/python%s/site-packages/',
            '/Library/Python/%s/site-packages/',
        ))


    for path in paths:
        if os.path.exists(path):
            return path
    if os.name!='posix':

        HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\library.zip','')

        windows_paths=[os.path.join(sys.prefix,'Lib\\site-packages'),\
                       os.path.join(HERE,'..','cyclone')]

        if os.getenv('TotoPath'):
            windows_paths.append(os.path.join(os.getenv('TotoPath'),'..'))
        for path in windows_paths:
            if os.path.exists(path):
                return path  
    
    print('no installation path found', file=sys.stderr)
    return None

def sphere_dist(from_lonlat,to_lonlats,radius_of_sphere=6378.1):

    #find vector in spherical coordinates from longitude and latitudes

    fx,fy,fz = sph2cart(from_lonlat[0]*np.pi/180,from_lonlat[1]*np.pi/180,radius_of_sphere)
    tx,ty,tz = sph2cart(to_lonlats[0]*np.pi/180,to_lonlats[1]*np.pi/180,radius_of_sphere)
    from_point=np.array([fx,fy,fz])
    to_points=np.array([tx.flatten(),ty.flatten(),tz.flatten()]).T



    from_point_m=np.tile(from_point,[to_points.shape[0],1])
    dot_prod=np.sum(from_point_m.T.conj()*to_points.T, axis=0)


    abs_from_point_m=(from_point_m[:,0]**2+from_point_m[:,1]**2+from_point_m[:,2]**2)**0.5;
    abs_to_points=(to_points[:,0]**2+to_points[:,1]**2+to_points[:,2]**2)**0.5

    phi=np.arccos(dot_prod/(abs_from_point_m*abs_to_points));
    dist=radius_of_sphere*phi
    return dist.reshape(to_lonlats[0].shape)


class Cyclone(object):

    def __init__(self,output_directory='/tmp/',
                    url='https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/access/netcdf/IBTrACS.ALL.v04r00.nc',
                    cyclone_file='/tmp/IBTrACS.ALL.v04r00.nc'):

        if not os.path.isfile(cyclone_file):
            self.download_cyclone(output_directory,url)

        self.default()
        self.read_cyclone(cyclone_file)
        self.add_categories()


    def default(self):
        self.min_cat=1
        self.method='from centre'
        self.rmw=None
        self.mask_before=12/24.
        self.mask_after=12/24.
        self.radius=500
        self.mask=False


    def download_cyclone(self,output_directory,url):
        urllib.request.urlretrieve(url, os.path.join(output_directory,'IBTrACS.ALL.v04r00.nc'))


    def read_cyclone(self,filename):
        ds = xr.open_dataset(filename)
        storm_ids = [''.join(name.astype(str))
                     for name in ds['sid'].values]
        sel_tracks = []
        years = np.array([int(iso_name[:4]) for iso_name in storm_ids])
        ind=years>YEAR0;
        storm_ids=np.array(storm_ids)

        storm_ids=storm_ids[ind]
        name=ds['name'][ind]
        lon=ds['lon'][ind]
        lat=ds['lat'][ind]

        t=ds['time'][ind,:]

        #Maximum Sustained Wind (MSW)provided by the US agencies
        Wmax=ds['usa_wind'][ind,:]*0.514444 #from knots to m/s

        #Minimum Central Pressure (MCP) provided by the US agencies
        Press=ds['usa_pres'][ind,:]#in mb or hPa


        #radius_of_tropical_cyclone_maximum_sustained_wind_speed provided by the US agencies
        RMW = ds['usa_wind'][ind,:];

        #Saffir-Simpson Hurricane Wind Scale Category
        category=ds['usa_sshs'][ind,:];
        self.cyclones={}

        self.cyclones['Name']=name.values
        self.cyclones['Longitude']=lon.values
        self.cyclones['Latitude']=lat.values
        self.cyclones['Radius']=RMW.values
        self.cyclones['sDate']=ds.time[ind,:].values
        self.cyclones['Pressure']=Press.values
        self.cyclones['MaximumWindSpeed']=Wmax.values
        self.cyclones['Category']=category.values



    def add_categories(self,):
        
        # print('.... Note: cyclone_track_functions: running ''add_categories''');
            
        if 'MaximumWindSpeed' in self.cyclones:
            
            AustBOMWindSpeed_Limits=[33, 43, 50, 58, 70]
            MaximumWindSpeed_m=np.tile(self.cyclones['MaximumWindSpeed'], [5,1,1])
            AustBOMWindSpeed_Limits_m=np.tile(np.array(AustBOMWindSpeed_Limits), [MaximumWindSpeed_m.shape[2],MaximumWindSpeed_m.shape[1],1]).T
            
            self.cyclones['Cat_AustBOMWindSpeed']=sum(MaximumWindSpeed_m>=AustBOMWindSpeed_Limits_m)
            self.cyclones['MaxCat_AustBOMWindSpeed']=np.max(self.cyclones['Cat_AustBOMWindSpeed'],1)

        if 'Pressure' in self.cyclones:
            AustBOMPressure_Limits=[1100, 985, 970, 950, 930];
            Pressure_m=np.tile(self.cyclones['Pressure'], [5,1,1])
            AustBOMPressure_Limits_m=np.tile(np.array(AustBOMPressure_Limits), [Pressure_m.shape[2],Pressure_m.shape[1],1]).T
            self.cyclones['Cat_AustBOMPressure']=sum(Pressure_m>=AustBOMPressure_Limits_m)
            self.cyclones['MaxCat_AustBOMPressure']=np.max(self.cyclones['Cat_AustBOMPressure'],1)

    def limit_categories_within_radius(self,pos):
        dist=sphere_dist(pos,[self.cyclones['Longitude'],self.cyclones['Latitude']]); #radius of earth in kilometers     
        within_radius=(dist<self.radius) & (self.cyclones['Cat_AustBOMWindSpeed']>self.min_cat)
        self.mask+=within_radius


    def remove_cyclones(self,t,pos):  
        #Calculate distance from location to cyclone track locations
        dist=sphere_dist(pos,[self.cyclones['Longitude'],self.cyclones['Latitude']]) #radius of earth in kilometers
        if self.rmw:
            within_radius=dist<self.cyclones['Radius']*self.rmw;
        else:
            within_radius=dist<self.radius

        self.mask+=within_radius

        mask=self.mask.flatten()

        T=date2num(self.cyclones['sDate']).flatten()

        T=T[mask]

        t=date2num(t)
        mask=t<0 # just to start with False array
        for i in range(0,len(T)):
            mask+=(t>=T[i]-self.mask_before) & (t<=T[i]+self.mask_after)
     

        return mask
        



if __name__ == '__main__':
    cy=Cyclone(cyclone_file='/tmp/IBTrACS.ALL.v04r00.nc')
    cy.limit_categories_within_radius([94.6,10.6])
    import pandas as pd
    dates = pd.date_range('1/1/2000', periods=8)
    msk=cy.remove_cyclones(dates,[94.6,10.6])
