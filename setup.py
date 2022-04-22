import setuptools
import requests 
import os, sys, site
import urllib.request
import platform

def binaries_directory():
    """Return the installation directory, or None"""


    if '--user' in sys.argv:
        paths = (site.getusersitepackages(),)
    else:
        py_version = '%s.%s' % (sys.version_info[0], sys.version_info[1])
        paths = (s % (py_version) for s in (

            sys.prefix + '/lib/python%s/dist-packages/',
            sys.prefix + '/lib/python%s/site-packages/',
            sys.prefix + '/local/lib/python%s/dist-packages/',
            sys.prefix + '/local/lib/python%s/site-packages/',
            '/Library/Python/%s/site-packages/',
        ))

    windows_paths=[os.path.join(sys.prefix,'Lib\\site-packages')]
    for path in paths:
        if os.path.exists(path):
            return path
    for path in windows_paths:
        if os.path.exists(path):
            return path        
    print('no installation path found', file=sys.stderr)
    return None

with open("README.rst", "r") as fh:
    long_description = fh.read()
pck=setuptools.find_packages(exclude=("totoview","totoview.*","totoView.py","_tests","_tools"))

package_data = {
    'core': ['core/*.yml'],
}


setuptools.setup(
    name="toto",
    version="1.1.0",
    author="Remy Zyngfogel",
    author_email="R.zyngfogel@calypso.science",
    description="A toolbox for processing timeseries'",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/calypso-science/Toto",
    packages=pck,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    data_files=[('toto/core', ['toto/core/attributes.yml'])]

)

### install Cyclone library from NOAA
url_palth='https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/access/netcdf/IBTrACS.ALL.v04r00.nc'
save_path=os.path.join(binaries_directory(),'IBTrACS.ALL.v04r00.nc')
print('Dowloading %s ' % url_palth)
if not os.path.isfile(save_path):
    urllib.request.urlretrieve (url_palth, save_path)
print('Cyclone file saved in : %s' % save_path)
