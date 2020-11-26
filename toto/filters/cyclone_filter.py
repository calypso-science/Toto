"""Remove cyclone evnt from a timeseries based on its position.
Needs:
  - lon/lat
  - NOAA Cyclone file (i.e IBTrACS.ALL.v04r00.nc)

Inputs:
  - radius of maximum wind
  - minimun category (default: 1)
  - mask radius from centre (default 500m)
  - time to mask before and after a cyclone passage (default 0.5 day)

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
                                      'radius of maximum wind':float(),\
                                      'mask radius from centre':500,\
                                    'Mode':{"from centre": True, "from wind radius":False}}):


    Lon=None
    if 'LonLat' in args:
        Lon=args['LonLat'][0]
        Lat=args['LonLat'][1]
    if Lon == None:
        Lon=args['Lon']
        Lat=args['Lat']

    cy=Cyclone(cyclone_file=args['cyclone file'])
    cy.limit_categories_within_radius([Lon,Lat])
    msk=cy.remove_cyclones(input_array.index,[Lon,Lat])

    input_array=input_array.loc[~msk]

    return input_array
