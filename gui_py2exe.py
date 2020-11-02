
import setuptools
from distutils.core import setup
from distutils.sysconfig import get_python_lib
import site
import os
from os.path import join, abspath, dirname
import py2exe
from glob import glob
import matplotlib
import sys
from totoview import __version__ as version
from distutils.filelist import findall
import os
import matplotlib
import zipfile
import mpl_toolkits.mplot3d
import mpl_toolkits.axisartist
import mpl_toolkits.axes_grid
import mpl_toolkits.axes_grid1
import appdirs
import pathlib
import tcl
import tkinter
PYTHON_SITEPACKAGES = get_python_lib()
#PYTHON_SITEPACKAGES = "C:\\Users\\papum\\Envs\\Toto3.7\\Lib\\site-packages"

matplotlibdatadir = matplotlib.get_data_path()
matplotlibdata = findall(matplotlibdatadir)
matplotlibdata_files = []
for f in matplotlibdata:
    dirname = os.path.join('matplotlib','mpl-data', f[len(matplotlibdatadir)+1:])
    matplotlibdata_files.append((os.path.split(dirname)[0], [f]))



# totoviewdata_files=[]
# for f in glob('totoview\\_tools\\*.*'):
#     dirname = os.path.join('totoview','_tools')
#     totoviewdata_files.append((dirname, [f]))

# for f in glob('toto\\plugins\\*.*'):
#     dirname = os.path.join('toto','plugins')
#     totoviewdata_files.append((dirname, [f]))

# for f in glob('toto\\core\\*.yml'):
#     dirname = os.path.join('toto','core')
#     totoviewdata_files.append((dirname, [f]))



# for f in glob(os.path.join(PYTHON_SITEPACKAGES,"dask","*.yaml")):
#     dirname = os.path.join('dask')
#     totoviewdata_files.append((dirname, [f]))

def better_copy_files(self, destdir):
    """Overriden so that things can be included in the library.zip."""

    #Run function as normal
    original_copy_files(self, destdir)

    #Get the zipfile's location
    if self.options.libname is not None:
        libpath = os.path.join(destdir, self.options.libname)

        #Re-open the zip file
        if self.options.compress:
            compression = zipfile.ZIP_DEFLATED
        else:
            compression = zipfile.ZIP_STORED
        arc = zipfile.ZipFile(libpath, "a", compression = compression)

        #Add your items to the zipfile
        for dest,item in matplotlibdata_files:
            if self.options.verbose:
                print("Copy File %s to %s" % (item[0], dest))
            arc.write(item[0], os.path.join(dest,os.path.basename(item[0])))
            #arc.write(item[0], os.path.join('pandas','plotting','_matplotlib',dest,os.path.basename(item[0])))
        
        # for dest,item in totoviewdata_files:
        #     if self.options.verbose:
        #         print("Copy File %s to %s" % (item[0], dest))
        #     arc.write(item[0], os.path.join(dest,os.path.basename(item[0])))
            

        arc.close()

        ## Here we add add and remove toto so all library gets included
        zin = zipfile.ZipFile (libpath, 'r')
        libpath_tmp=os.path.join(destdir,'libtmp.zip')
        zout = zipfile.ZipFile (libpath_tmp, 'w')
        for item in zin.infolist():
            buffer = zin.read(item.filename)
            if not ('toto/' in item.filename):
                zout.writestr(item, buffer)
        zout.close()
        zin.close()

        os.remove(libpath)
        os.rename(libpath_tmp,libpath)


        ## here we need to copy the files that used package_resourec



original_copy_files = py2exe.runtime.Runtime.copy_files
py2exe.runtime.Runtime.copy_files = better_copy_files



GDAL_DIR = "C:\\Program Files\\GDAL"
MSVC_DIR = "C:\\Program Files (x86)\\Microsoft Visual Studio 9.0\\VC\\redist\\x86\\Microsoft.VC90.CRT"
MSVC_DIR = "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\BuildTools\\VC\\Redist\\MSVC\\14.27.29016\\x86\\Microsoft.VC142.CRT"
DEST_DIR = "compiled64"


sys.path.extend([MSVC_DIR, GDAL_DIR])

options = {
    "py2exe": {
        "bundle_files":3,
        "dist_dir": DEST_DIR,
        "skip_archive": True,
        "ascii": False,
        "xref": False,
        "includes": ["dask","six",'matplotlib',"mpl_toolkits.axisartist","mpl_toolkits.axes_grid","mpl_toolkits.axes_grid1",'pandas','PyQt5','mplcyberpunk','PyQt5.QtCore','PyQt5.QtWidgets','appdirs'],
        "dll_excludes": [],
        "excludes": ['_gtkagg', '_tkagg'],
        "packages" : ['numpy','matplotlib', 'pandas','future','scipy','xarray',
                      'PyQt5', 'windrose','attrdict','ctypes', 'openpyxl',
                      'yaml', "numba","numdifftools","utide","wafo","netCDF4",
                      "encodings","mplcyberpunk","grid_strategy","mpl_toolkits.mplot3d",
                      "totoview","totoview.core","totoview.dialog","totoview.inputs"],
                      # "toto","toto.inputs",
                      # "toto.plugins.extreme","toto.plugins.plots","toto.plugins.statistics",
                      # "toto.plugins.tide","toto.plugins.tide","toto.plugins.transformations",
                      # "toto.plugins.wave","toto.plugins.woodside"],
    }
}


data_files = [
    ('', glob(r'C:\\Windows\\SysWOW64\\msvcp100.dll')),
    ('', glob(r'C:\\Windows\\SysWOW64\\msvcr100.dll')),
    #('toto\\core', glob('toto\\core\\*.yml*')),
    ('totoview\\_tools', glob('totoview\\_tools\\*.*')),
    ("Microsoft.VC90.CRT", glob(os.path.join(MSVC_DIR, '*.*'))),
    (r"platforms", glob(os.path.join(PYTHON_SITEPACKAGES, "PyQt5", "Qt", "plugins", "platforms","*.dll"))),
    (r"", glob(os.path.join(PYTHON_SITEPACKAGES, "PyQt5", "Qt", "plugins", "imageformats","*.dll"))),
    (r"", glob(os.path.join(PYTHON_SITEPACKAGES, "PyQt5", "Qt", "plugins", "iconengines","*.dll"))),
    (r"", glob(os.path.join(PYTHON_SITEPACKAGES, "PyQt5", "Qt", "bin", "Qt*.dll"))),
    (r"", glob(os.path.join(PYTHON_SITEPACKAGES, "scipy", "extra-dll", "*.dll"))),
    ("mplcyberpunk\\data", glob(os.path.join(PYTHON_SITEPACKAGES,"mplcyberpunk","data",'*'))),
    ("dask", glob(os.path.join(PYTHON_SITEPACKAGES,"dask",'*.yaml'))),
    ("llvmlite\\binding", glob(os.path.join(PYTHON_SITEPACKAGES,"llvmlite","binding",'*.dll'))),
    ("utide\\data", glob(os.path.join(PYTHON_SITEPACKAGES,"utide","data",'*.*'))),
    ]

print(data_files)

setup(
    name="totoView",
    version=version,
    description=u"totoView - Calypso Science/MetOcean Solutions",
    author="Calypso Science",
    console=['totoView.py'],
    #zipfile=None,
    # windows=[{'script':'totoView.py',
    #          'icon_resources': [(1, "totoview\\_tools\\toto.ico")],
    #          }],
    options=options,
    data_files=data_files,
)


