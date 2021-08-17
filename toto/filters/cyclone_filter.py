"""Remove cyclone evnt from a timeseries based on its position.
    Parameters
    ~~~~~~~~~~

    Lon : float
        Longitude of the timeseries
    Lat : float
        Latitude of the timeseries
    cyclone file : str
        cyclone file downloaded from the NOAA
    minimun category : int 
        Ignore all cyclone below this category
    radius of maximum wind : float
        Use 
    time to mask before a cyclone passage (in days): float
        Once a cyclone is detected, the timeseries will be mask by n days before the cyclone is above the Lat/Lon position
    time to mask after a cyclone passage (in days) : float
        Once a cyclone is detected, the timeseries will be mask by n days after the cyclone is above the Lat/Lon position
    mask radius from centre : float
        Mask if a cyclone is within a distance from the centre
    Mode : str default "from centre", "from wind radius" 
        Choose to mask using the wind radius or a distance from the centre

    Notes
    ~~~~~
    
        * The cyclone library from NOAA <https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/access/netcdf/IBTrACS.ALL.v04r00.nc>_ needs to be downloaded.
          By default it using IBTrACS.ALL.v04r00.nc that is saved during the install procedure

    Examples:
    ~~~~~~~~~

    >>> # Time series location
    >>> lon=115.3085
    >>> lat=19.8892
    >>> # import Cyclone module
    >>> CYCLONE_FILE=os.path.join(binaries_directory(),'IBTrACS.ALL.v04r00.nc')
    >>> cy=Cyclone(cyclone_file=CYCLONE_FILE)
    >>> cy.min_cat=1 # Minimum category to use
    >>> cy.rmw=None # radius_of_tropical_cyclone_maximum_sustained_wind_speed if not set it will use radius in meters
    >>> cy.radius=500 # radius around the cente to mask in meter
    >>> cy.mask_before=12/24. # hours before a cyclone to mask
    >>> cy.mask_after=12/24. # hours after a cyclone to mask
    >>> # mask all timestep within cy.radius with cyclone above or equal the minimum category 
    >>> cy.limit_categories_within_radius([lon,lat]) 
    >>> # create the mask
    >>> msk=cy.remove_cyclones(df[0].index,[lon,lat])
    >>> # Apply the mask
    >>> df_no_cyclone=df[0].loc[~msk] 

"""

import numpy as np
from ..core.cyclone_mask import Cyclone,binaries_directory
import os

CYCLONE_FILE=os.path.join(binaries_directory(),'IBTrACS.ALL.v04r00.nc')

def cyclone_filter(input_array,args={'Lon':float(),'Lat':float(),'cyclone file':CYCLONE_FILE,\
                                       'minimun category':1,\
                                      'radius of maximum wind':float(),\
                                      'time to mask before a cyclone passage (in days)':0.5,\
                                                      'time to mask after a cyclone passage (in days)':0.5,\
                                      'mask radius from centre':500,\
                                    'Mode':{"from centre": True, "from wind radius":False}}):


    Lon=None
    if 'LonLat' in args:
        Lon=args['LonLat'][0]
        Lat=args['LonLat'][1]
    if Lon == None:
        Lon=args['Lon']
        Lat=args['Lat']

    if isinstance(Lon,np.ndarray):
      Lon=Lon[0]
      Lat=Lat[0]

    cy=Cyclone(cyclone_file=args['cyclone file'])
    cy.limit_categories_within_radius([Lon,Lat])
    msk=cy.remove_cyclones(input_array.index,[Lon,Lat])

    input_array=input_array.loc[~msk]

    return input_array
