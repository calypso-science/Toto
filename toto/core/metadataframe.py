
from .attributes import attrs

class MetadataFrame(dict):

    def __init__(self,Vars='hs'):
        if type(Vars) != type(list):
            Vars=[Vars]

        for varname in Vars:
            self[varname]={}
            self[varname].update(attrs['ATTRS'].get(varname,attrs['ATTRS']['default']))
            self[varname].update(attrs['OPT'])
            self[varname]['short_name']=varname



    def stuff(self):
        pass
        """Do my stuff"""

