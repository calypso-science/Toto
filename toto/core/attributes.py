"""Standarise Metadata attributes.
"""

import os

import yaml

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\library.zip','')

with open(os.path.join(HERE, "attributes.yml")) as stream:
    attrs = AttrDict(yaml.load(stream, yaml.SafeLoader))


def set_metadata_attributes(Metadata):
    """
    Standarise CF attributes in Toto variables
    """
    for varname, varattrs in attrs.ATTRS.items():
        try:
            Metadata[varname].attrs = varattrs
        except Exception as exc:
            pass


if __name__ == '__main__':
	Metadata={}
	set_metadata_attributes(Metadata)
	