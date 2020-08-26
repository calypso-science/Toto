import numpy as np
import datetime



def get_opt(var,label_name,default):
    if hasattr(var,label_name):
        label=getattr(var,label_name)
    else:
        label=''
    
    if label=='':
        label=default

    return label
def get_number_of_loops(time_blocking):

    if 'annual' in time_blocking.lower():
        number_of_loops=1
        identidifers=['Annual']
        month_identidier=[np.arange(1,13,1)]
    elif 'seasonal' in time_blocking.lower():
        identidifers,month_identidier=get_seasons(time_blocking)
        number_of_loops=4+1
        month_identidier.append([np.arange(1,13,1)])
        identidifers.append('Annual')
    elif 'monthly' in time_blocking.lower():
        identidifers=[]
        month_identidier=[]
        for m in range(1,13):
            identidifers.append(datetime.date(1900, m, 1).strftime('%B'))
            month_identidier.append([m])
        identidifers.append('Annual')
        number_of_loops=12+1
        month_identidier.append([np.arange(1,13,1)])



    return number_of_loops,identidifers,month_identidier

                

def get_seasons(typ):
    seasons_name=['Summer','Autumn','Winter','Spring']
    if 'south' in typ.lower():
        seasons=[[12,1,2],[3,4,5],[6,7,8],[9,10,11]]
    else:
        seasons=[[6,7,8],[9,10,11],[12,1,2],[3,4,5]]
    return seasons_name,seasons    

def get_increment(data,s):
    if len(s)>3:
        interval=s
    else:
        if len(s)==3:
            interval=np.arange(s[0],s[2]+s[1],s[1])
        else:
            upper_limit=np.ceil(np.max(data/s[1]))*s[1]
            interval=np.arange(s[0],upper_limit+s[1],s[1])
    return interval

def wavenuma(ang_freq, water_depth):
    """Chen and Thomson wavenumber approximation."""
    k0h = 0.10194 * ang_freq * ang_freq * water_depth
    D = [0, 0.6522, 0.4622, 0, 0.0864, 0.0675]
    a = 1.0
    for i in range(1, 6):
        a += D[i] * k0h ** i
    return (k0h * (1 + 1.0 / (k0h * a)) ** 0.5) / water_depth
   
  


def cart2sph(x,y,z):
    azimuth = np.arctan2(y,x)
    elevation = np.arctan2(z,np.sqrt(x**2 + y**2))
    r = np.sqrt(x**2 + y**2 + z**2)
    return azimuth, elevation, r

def sph2cart(azimuth,elevation,r):
    x = r * np.cos(elevation) * np.cos(azimuth)
    y = r * np.cos(elevation) * np.sin(azimuth)
    z = r * np.sin(elevation)
    return x, y, z

def cart2pol(x,y):
    th = np.arctan2(y,x)
    r = np.sqrt(x**2 + y**2)
    return th,r

    
def dir_interval(dir_swath=45,mode='centred'):

#Calculates directional intervals based on dir_swath which must 
#be a whole number divisor of 360.
#mode can be either "centred" or "not-centred" 
#Default is centred

# here you specify the directional swath that you wish to analyse
    if dir_swath==0:
        dir_swath=360;

    if 360 % dir_swath !=0:
        print('The chosen interval is not a multiple of 360')
        raise
    interval=[]
    if mode == 'centred' or mode=='centered':
        for i in range(0,int(360//dir_swath)):
            if i==0:
                interval.append(360-(dir_swath/2))
            elif i==1:
                interval.append(dir_swath/2);
            elif i>1:
                interval.append(interval[i-1]+dir_swath)
            
        interval.append(interval[i]+dir_swath-1e-10) # this is a fudge factor (-1e-10) but is a good soln.  
    else: # 'not-centred'
        for i in range(0,int(360//dir_swath)):
            if i==0:
                interval.append(0)
            else:
                interval.append(interval[i-1]+dir_swath)
            
        
        interval.append(interval[i]+dir_swath)

    return interval

def degToCompass(num):
    if isinstance(num,list) or isinstance(num,np.array):
        rads = np.deg2rad(num)  
        av_sin = np.mean(np.sin(rads))  
        av_cos = np.mean(np.cos(rads))  
        ang_rad = np.arctan2(av_sin,av_cos)  
        num = np.mod(np.round(np.rad2deg(ang_rad),1),360)


    val=int((num/22.5)+.5)

    arr=["N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return arr[(val % 16)]

if __name__ == '__main__':
    #print(dir_interval(dir_swath=22.5,mode='centred'))
    #print(dir_interval(dir_swath=45,mode='not-centred'))

    print(degToCompass([350,3,10]))
