import numpy as np

from ..core.cyclone_mask import Cyclone

def cyclone_filter(input_array,args={'Lon':float(),'Lat':float(),'cyclone file':'/tmp/IBTrACS.ALL.v04r00.nc',\
                                       'minimun category':1,\
                                      'radius of maximum wind':float(),\
                                      'time to mask before a cyclone passage (in days)':0.5,\
                                                      'time to mask after a cyclone passage (in days)':0.5,\
                                      'radius of maximum wind':float(),\
                                      'mask radius from centre':500,\
                                    'Mode':{"from centre": True, "from wind radius":False}}):




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
