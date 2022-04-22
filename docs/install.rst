.. image:: _static/calypso.png
   :width: 150 px
   :align: right

=============
Installation:
=============

Where to get it
---------------
The source code is currently hosted on GitHub at: https://github.com/calypso-science/Toto

It can be clone by doing:
.. code:: bash
	git clone https://github.com/calypso-science/Toto.git

Note: This software works with python > 3 only

Install from sources
--------------------
Install requirements. Navigate to the base root of toto and execute:

.. code:: bash

   pip install -r requirements.txt


Then install toto:

.. code:: bash

   python setup.py install

Installation tutorial:

`TOTO`_


Adding the extra pluggins
-------------------------

In order to add the extra module, first you need to contact to get your licenses:

•	Brett Beamsley: b.beamsley@metocean.co.nz

•	Remy Zyngfogel: r.zyngfogel@calypso.science

Then you will be able to access the extra module repo via github
To install them naviguate the toto_plugins folder and type:

.. code:: bash
   python add_module.py

.. _`TOTO`: https://youtu.be/PB3O_AQ0Ots