#!/usr/bin/env python
from __future__ import absolute_import
import sys


def main(filenames=[],dataframes=None):
    import totoview
    totoview.show(filenames=filenames,dataframe=dataframes)

if __name__ == '__main__':
    main(sys.argv[1:])