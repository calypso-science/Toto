Toto
===========
Python library for ocean timeseries analysis spectra.


Main contents:
--------------
- inputs       : reader function to load files.
- outputs      : outputs function to save files.
- filter       : filtering toolbox
- interpolation: interpolation toolbox
- selections   : selection toolbox
- plugins      : user defined plugins

Install:
--------
Where to get it
~~~~~~~~~~~~~~~
The source code is currently hosted on GitHub at: https://github.com/calypso-science/Toto

Install from sources
~~~~~~~~~~~~~~~~~~~~
The Wafo toolbox need to be installed:
https://github.com/wafo-project/pywafo

Install requirements. Navigate to the base root of toto and execute:

.. code:: bash

   pip install -r requirements.txt


Then install toto:

.. code:: bash

   python setup.py install


Data requirements:
------------------
toto methods require a Panda dataframe:


Examples:
---------

Define a panda datafame and transform from UV to SPD and DIR:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

	import numpy as np
	import pandas as pd
	import toto
	dates = pd.date_range('1/1/2000', periods=360)
	arr=np.random.randn(360, 2)
	df = pd.DataFrame(arr,index=dates, columns=['U', 'V'])
	df=df.DataTransformation.uv_to_spddir(u='U',v='V')


Download HyCOM data as a panda datafame and extract common statistics:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

	import xarray
	import toto
	url='https://tds.hycom.org/thredds/dodsC/GLBy0.08/latest?time[0:1:100],surf_el[0:1:100][2000][3000]'
	xar=xarray.open_dataset(url)
	df=xar.to_dataframe()
	df.reset_index(inplace=True)
	df.set_index('time',inplace=True,drop=False)
	df.Statistics.common_stats(mag='surf_el')