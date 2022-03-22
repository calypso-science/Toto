"""Define module attributes.
- Defining packaging attributes accessed by setup.py
- Making reading functions available at module level
"""

__version__ = "1.0"
__author__ = "Calypso Science"
__contact__ = "r.zyngfogel@calypso.science"
__url__ = "calyps.science"
__description__ = "Ocean timeSeries tools"
__keywords__ = "ocean panda time-series statistics analysis"


def _import_functions(pkgname="inputs",name='read'):
    """Make read functions available at module level.
    Functions are imported here if:
        - they are defined in a module toto.input.{modname}
        - they are named as read_{modname}
    """
    import os
    import sys
    import glob
    from importlib import import_module

    here = os.path.dirname(os.path.abspath(__file__)).replace('\\library.zip','')
    for filename in glob.glob1(os.path.join(here, pkgname), "*.py"):
        module = os.path.splitext(filename)[0]
        if module == "__init__":
            continue
        func_name = "{}_{}".format(name,module)
        try:
            # globals()[func_name] = getattr(
            #     import_module("toto.{}.{}".format(pkgname, module)), func_name
            # )
            import_module("toto.{}.{}".format(pkgname, module))
        except Exception as exc:
            print("Cannot import {} function {}:\n{}".format(name,func_name, exc))

def _import_plugins(pkgname="inputs",name='read'):
    import os
    import sys
    import glob
    from importlib import import_module
    here = os.path.dirname(os.path.abspath(__file__)).replace('\\library.zip','')
    for dirs in os.listdir(os.path.join(here, pkgname)):
        if os.path.isdir(os.path.join(here, pkgname,dirs)):
            for filename in glob.glob1(os.path.join(here, pkgname,dirs), "*.py"):
                module = os.path.splitext(filename)[0]
                if module.startswith('_'):
                    continue

                tmp=import_module("toto.{}.{}.{}".format(pkgname,dirs, module))


                for Clss in [x for x in dir(tmp) if x[0].isupper()]:
                    clss=getattr(tmp,Clss)
                    for fct in [y for y in dir(clss) if not y.startswith('_')]:
                        try:
                            setattr(getattr(globals()['plugins'],dirs),fct,getattr(clss,fct))
                        except Exception as exc:
                            print("Cannot import {}.{} function {}:\n{}".format(dirs,tmp,fct, exc))



_import_functions(pkgname="inputs",name='read')
_import_functions(pkgname="outputs",name='outputs')
_import_functions(pkgname="filters",name='filters')
_import_functions(pkgname="interpolations",name='interp')
_import_functions(pkgname="selections",name='select')
_import_plugins(pkgname="plugins",name='plug')
# for fct in [x for x in dir(getattr(globals()['plugins'],'extreme'))]:
#     if hasattr(getattr(getattr(globals()['plugins'],'extreme'),fct),'__name__'):
#         if getattr(getattr(globals()['plugins'],'extreme'),fct).__name__ not in ['do_extreme_adjusted','do_extreme','extreme_water_elevation','distribution_shape']:
#             delattr(getattr(globals()['plugins'],'extreme'),fct)
#     else:
#         delattr(getattr(globals()['plugins'],'extreme'),fct)

# toto.plugins.extreme.zipf.__class__==toto.plugins.extreme.distribution_shape.__class__