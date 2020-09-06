"""Access functions to read time series from data files.
The following structure is expected:
    - Reading functions for each data file type defined in specific modules
    - Modules named as {datatype}.py, e.g. text.py
    - Functions named as read_{dataname}, e.g. read_text
All functions defined with these conventions will be dynamically
imported at the module level
"""