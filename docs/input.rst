.. image:: _static/calypso.png
   :width: 150 px
   :align: right

Input
=====

.. py:module:: toto.input

Functions to read time series from file into
:py:class:`~toto.core.totoframe`.

The input functions allow abstracting away the format the data are
stored on disk and loading them into a standard Panda DataFrame object. The methods
adds attribute to the dataframe such as unit, latitude,longitude.

Reading functions are defined in modules within
:py:mod:`toto.input` subpackage. The functions can be accessed as:

.. code:: python

    from toto.inputs.nc import NCfile
    dset = NCfile('myfile.nc')_toDataFrame()

The following convention is expected for defining reading functions:

- Funcions for different file types are defined in different modules within
  :py:mod:`toto.input` subpackage.
- Modules are named as `filetype`.py, e.g., ``nc.py``.
- Classes are named as `filetype`file, e.g., ``NCfile``.
- Each class must have a  `_toDataFrame()` function

The following input functions are currently available:

Generic NetCDF:
---------------
.. automodule:: toto.inputs.nc
   :noindex:

MSL NetCDF:
-----------
.. automodule:: toto.inputs.msl
   :noindex:

LINZ NetCDF:
------------
.. automodule:: toto.inputs.linz
   :noindex:

MOET NetCDF:
------------
.. automodule:: toto.inputs.moet
   :noindex:

MATLAB
------

.. automodule:: toto.inputs.mat
   :noindex:

TRYAXIS
-------

.. automodule:: toto.inputs.tryaxis
   :noindex:

TEXT
----

.. automodule:: toto.inputs.txt
   :noindex:

CONSTITUENTS FILE
-----------------

.. automodule:: toto.inputs.cons
   :noindex:

EXCEL FILE
----------

.. automodule:: toto.inputs.xls
   :noindex:

RSK FILE
----------

.. automodule:: toto.inputs.rsk
   :noindex: