

import pandas as pd


#@pd.api.extensions.register_dataframe_accessor("toto")
class TotoFrame(object):
    def __init__(self, panda_obj, dim_map=None):
        """Define toto attributes."""

        self._obj = panda_obj

    def test(self):
        print('remy')