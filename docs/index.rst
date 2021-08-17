.. Toto documentation master file, created by
   sphinx-quickstart on Fri Aug 13 15:27:10 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: _static/calypso.png
   :width: 150 px
   :align: right


TOTO
====

.. image:: _static/logo.ico
   :width: 200 px
   :align: center



TOTO is a toolbox developed by Calypso Science Ltd and MetOcean Solution Ltd.
It includes all the functions developed over the years to realized ocean timeseries statistics, extreme analysis and data representation. 
TOTO extends panda’s `DataFrame`_ with methods to manipulate, filter and calculate various ocean science statistics.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

    How to install <install>
    Conventions <convention>
    Inputs <input>
    Filter functions <source/toto.filters>
    Interpolation functions <source/toto.interpolations>
    Selection functions <source/toto.selections>
    Plugins <source/toto.plugins>
    Customization <customize>
    Gallery <gallery/index>
    support <support>

.. toctree::
    :maxdepth: 2
    :caption: API documentation:

    Toto open-source <source/modules>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _`DataFrame`: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html