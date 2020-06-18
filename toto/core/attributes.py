"""Standarise Metadata attributes.
"""

import os

import yaml
from attrdict import AttrDict

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "attributes.yml")) as stream:
    attrs = AttrDict(yaml.load(stream, yaml.SafeLoader))


def set_metadata_attributes(Metadata):
    """
    Standarise CF attributes in specarray variables
    """
    for varname, varattrs in attrs.ATTRS.items():
        try:
            Metadata[varname].attrs = varattrs
        except Exception as exc:
            pass


if __name__ == '__main__':
	Metadata={}
	set_metadata_attributes(Metadata)
	