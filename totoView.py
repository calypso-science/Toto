#!/usr/bin/env python
from __future__ import absolute_import
import sys

def main(inputfiles=[]):
    import totoview
    totoview.show(filenames=inputfiles)

if __name__ == '__main__':
    main(sys.argv[1:])