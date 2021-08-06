def resampler(input_array,args={'value':'1H',\
	'method':{"asfreq":False,"bfill":False,"ffill":False,\
	"pad":True,"sum":False,"mean":False,"max":False,"min":False,"nearest": True}}):


    method=args['method']
    if method=='nearest':
       input_array = input_array.resample(args['value']).nearest()
    elif method=='pad':
       input_array = input_array.resample(args['value']).pad()    
    elif method=='sum':
       input_array = input_array.resample(args['value']).sum() 
    elif method=='min':
       input_array = input_array.resample(args['value']).min() 
    elif method=='max':
       input_array = input_array.resample(args['value']).max() 
    elif method=='mean':
       input_array = input_array.resample(args['value']).mean() 
    elif method=='ffill':
       input_array = input_array.resample(args['value']).ffill() 
    elif method=='bfill':
       input_array = input_array.resample(args['value']).bfill() 
    elif method=='as_freq':
       input_array = input_array.resample(args['value']).asfreq() 
    return input_array




