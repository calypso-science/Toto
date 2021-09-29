.. image:: _static/calypso.png
   :width: 150 px
   :align: right

=============
Installation:
=============

Where to get it
--------------------
The source code is currently hosted on GitHub at: https://github.com/calypso-science/Toto

Module requirements:
--------------------

WAFO
~~~~
The PyWafo toolbox need to be installed if you are going to use the Extreme Value Analysis plugins.
If you are using WINDOWS I recommend using the totoview_nototo.exe as the WAFO toolbox is harder to install.
To install it please refer to the `PyWafo`_ GitHub page 

Install from sources
--------------------
Install requirements. Navigate to the base root of toto and execute:

.. code:: bash

   pip install -r requirements.txt


Then install toto:

.. code:: bash

   python setup.py install



Using the compiled version
--------------------------
There are two versions of TOTOVIEW that are already compiled for Windows user.
They can be found on the GitHub page (https://github.com/calypso-science/Totoview/releases):

• totoview_withtoto.exe.

 This version will install TOTO and TOTOVIEW. No need to install TOTO, it is included in it. However, you will need to wait for a new release to update your code

• totoview_nototo.exe.

 This version will install TOTOVIEW and TOTO’s requirement. You still need to install TOTO but you can skip the requirement installation. This is easier to update TOTO's code, just need to pull the updated code from GitHub and re-install TOTO.


Adding the extra pluggins
-------------------------

In order to add the extra module, first you need to contact to get your licenses:

•	Brett Beamsley: b.beamsley@metocean.co.nz

•	Remy Zyngfogel: r.zyngfogel@calypso.science

Then you will be able to access the extra module repo via github
To install them naviguate the toto_plugins folder and type:

.. code:: bash
   python add_module.py

.. _`PyWafo`: https://github.com/wafo-project/pywafo