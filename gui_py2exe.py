

from distutils.core import setup
from distutils.sysconfig import get_python_lib
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

matplotlibdatadir = matplotlib.get_data_path()
matplotlibdata = findall(matplotlibdatadir)
matplotlibdata_files = []
for f in matplotlibdata:
    dirname = os.path.join('matplotlib','mpl-data', f[len(matplotlibdatadir)+1:])
    matplotlibdata_files.append((os.path.split(dirname)[0], [f]))

totoviewdata_files=[]
totoviewdata=glob('totoview\\_tools\\*.*')
for f in totoviewdata:
    dirname = os.path.join('totoview','_tools')
    totoviewdata_files.append((dirname, [f]))


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
        
        for dest,item in totoviewdata_files:
            if self.options.verbose:
                print("Copy File %s to %s" % (item[0], dest))
            arc.write(item[0], os.path.join(dest,os.path.basename(item[0])))
            

        arc.close()


original_copy_files = py2exe.runtime.Runtime.copy_files
py2exe.runtime.Runtime.copy_files = better_copy_files




GDAL_DIR = "C:\\Program Files\\GDAL"
MSVC_DIR = "C:\\Program Files (x86)\\Microsoft Visual Studio 9.0\\VC\\redist\\x86\\Microsoft.VC90.CRT"
MSVC_DIR = "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\BuildTools\\VC\\Redist\\MSVC\\14.27.29016\\x86\\Microsoft.VC142.CRT"
DEST_DIR = 'compiled64'
PYTHON_SITEPACKAGES = get_python_lib()

sys.path.extend([MSVC_DIR, GDAL_DIR])

options = {
    "py2exe": {
        "bundle_files":3,
        "dist_dir": DEST_DIR,
        "skip_archive": True,
        "ascii": False,
        "xref": False,
        "includes": ["six",'matplotlib','pandas','PyQt5','PyQt5.QtCore','PyQt5.QtWidgets'],
        "dll_excludes": [],
        # ['libiomp5md.dll',
        #                 'libifcoremd.dll','libmmd.dll' , 'svml_dispmd.dll',
        #                 'libifportMD.dll','libgdk-win32-2.0-0.dll',
        #                 'libgobject-2.0-0.dll', 'libgdk_pixbuf-2.0-0.dll',
        #                 'api-ms-win-core-delayload-l1-1-0.dll',
        #                 'api-ms-win-core-delayload-l1-1-1.dll',
        #                 'api-ms-win-core-debug-l1-1-0.dll',
        #                 'api-ms-win-core-errorhandling-l1-1-0.dll',
        #                 'api-ms-win-core-errorhandling-l1-1-1.dll',
        #                 'api-ms-win-core-file-l1-2-1.dll',
        #                 'api-ms-win-core-heap-l1-1-0.dll',
        #                 'api-ms-win-core-heap-l1-2-0.dll',
        #                 'api-ms-win-core-heap-l2-1-0.dll',
        #                 'api-ms-win-core-handle-l1-1-0.dll',
        #                 'api-ms-win-core-libraryloader-l1-1-0.dll',
        #                 'api-ms-win-core-libraryloader-l1-2-0.dll',
        #                 'api-ms-win-core-libraryloader-l1-2-1.dll',
        #                 'api-ms-win-core-localregistry-l1-1-0.dll',
        #                 'api-ms-win-core-localization-l1-2-1.dll',
        #                 'api-ms-win-core-localization-obsolete-l1-2-0.dll',
        #                 'api-ms-win-core-interlocked-l1-1-0.dll',
        #                 'api-ms-win-core-misc-l1-1-0.dll',
        #                 'api-ms-win-core-processthreads-l1-1-0.dll',
        #                 'api-ms-win-core-processthreads-l1-1-1.dll',
        #                 'api-ms-win-core-processthreads-l1-1-2.dll',
        #                 'api-ms-win-core-profile-l1-1-0.dll',
        #                 'api-ms-win-core-realtime-l1-1-0.dll',
        #                 'api-ms-win-core-registry-l1-1-0.dll',
        #                 'api-ms-win-core-rtlsupport-l1-1-0.dll',
        #                 'api-ms-win-core-string-l1-1-0.dll',
        #                 'api-ms-win-core-string-l2-1-0.dll',
        #                 'api-ms-win-core-string-obsolete-l1-1-0.dll',
        #                 'api-ms-win-core-synch-l1-1-0.dll',
        #                 'api-ms-win-core-synch-l1-2-0.dll',
        #                 'api-ms-win-core-synch-l1-2-1.dll',
        #                 'api-ms-win-core-sysinfo-l1-1-0.dll',
        #                 'api-ms-win-core-sysinfo-l1-2-1.dll',
        #                 'api-ms-win-crt-string-l1-1-0.dll',
        #                 'api-ms-win-crt-private-l1-1-0.dll',
        #                 'api-ms-win-crt-runtime-l1-1-0.dll',
        #                 'api-ms-win-eventing-provider-l1-1-0.dll',
        #                 'api-ms-win-security-base-l1-1-0.dll',
        #                 'api-ms-win-security-base-l1-2-0.dll',
        #                 'api-ms-win-security-activedirectoryclient-l1-1-0.dll',
        #                 'libgdk_pixbuf-2.0-0.dll'],
        "excludes": ['_gtkagg', '_tkagg'],
        "packages" : ['numpy','matplotlib', 'pandas','future','scipy','xarray',
                      'PyQt5', 'windrose','attrdict','ctypes', 'openpyxl',
                      'yaml', "numba","numdifftools","utide","wafo","netCDF4",
                      "encodings","mplcyberpunk","grid_strategy",
                      "totoview","totoview.core","totoview.dialog","totoview.inputs"
                      ],
    }
}


data_files = [
    ('', glob(r'C:\\Windows\\SysWOW64\\msvcp100.dll')),
    ('', glob(r'C:\\Windows\\SysWOW64\\msvcr100.dll')),
    #('', glob('windlls\*.dll')),iipyt
    #('', glob('Manual.pdf')),
    #('', glob('ffmpeg.win32.exe')),
    ('totoview\\_tools', glob('totoview\\_tools\\*.*')),
    #('', glob('LICENSE.txt')),
    ("Microsoft.VC90.CRT", glob(os.path.join(MSVC_DIR, '*.*'))),
    (r"platforms", glob(os.path.join(PYTHON_SITEPACKAGES,'PyQt5','Qt','plugins','platforms','qwindows.dll'))),
    #(r"", glob(join(PYTHON_SITEPACKAGES, 'numpy','DLLs','*.dll'))),
    ]

print(data_files)

setup(
    name="totoView",
    version=version,
    description=u"totoView - Calypso Science/MetOcean Solutions",
    author="Calypso Science",
    console=['totoView.py'],
    #windows=[{'script':'totoView.py',
    #          'icon_resources': [(1, "_tools/toto.ico")],
    #          }],
    options=options,
    data_files=data_files,
)


