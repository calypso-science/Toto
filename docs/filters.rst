.. image:: _static/calypso.png
   :width: 150 px
   :align: right

Filters
=======

.. py:module:: toto.filters

Functions to filter and clean time series

Filters functions are defined in modules within
:py:mod:`toto.filters` subpackage. The functions can be accessed as:

.. code:: python

    from toto.filters import despike_phasespace3d
    dset = NCfile('myfile.nc')_toDataFrame()
    dset['phasespace3d']=despike_phasespace3d.despike_phasespace3d(
                       dset['signal'].copy())

The following filters functions are currently available:

•	:doc:`Bandpass filter  <source/toto.filters.bandpass_filter>`

•	:doc:`Cyclone filter <source/toto.filters.cyclone_filter>`

•	:doc:`Despike phasespace3d <source/toto.filters.despike_phasespace3d>`

•	:doc:`Detrend <source/toto.filters.detrend>`

•	:doc:`Moving average <source/toto.filters.moving_average>`

•	:doc:`Spike removal <source/toto.filters.spike_removal>`

•	:doc:`Lanczos filter <source/toto.filters.lanczos_filter>`