
from .attributes import attrs

class MetadataFrame(dict):

    def __init__(self,varnames='hs'):
        if type(varnames) != type(list):
            varnames=[varnames]

        for varname in varnames:
            self[varname]={}
            self[varname]=attrs['ATTRS'].get(varname,attrs['ATTRS']['default'])
            self[varname].update(attrs['OPT'])
            self[varname]['short_name']=varname


    def stuff(self):
        pass
        """Do my stuff"""

