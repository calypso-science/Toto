"""Define module attributes.
- Defining packaging attributes accessed by setup.py
- Making reading functions available at module level
"""

__version__ = "1.0"
__author__ = "Calypso Science"
__contact__ = "r.zyngfogel@calypso.science"
__url__ = ""
__description__ = "Ocean timeSeries tools"
__keywords__ = "ocean panda time-series statistics analysis"


def _import_read_functions(pkgname="inputs"):
    """Make read functions available at module level.
    Functions are imported here if:
        - they are defined in a module toto.input.{modname}
        - they are named as read_{modname}
    """
    import os
    import sys
    import glob
    from importlib import import_module

    here = os.path.dirname(os.path.abspath(__file__))
    for filename in glob.glob1(os.path.join(here, pkgname), "*.py"):
        module = os.path.splitext(filename)[0]
        if module == "__init__":
            continue
        func_name = "read_{}".format(module)
        try:
            # globals()[func_name] = getattr(
            #     import_module("toto.{}.{}".format(pkgname, module)), func_name
            # )
            import_module("toto.{}.{}".format(pkgname, module))
        except Exception as exc:
            print("Cannot import reading function {}:\n{}".format(func_name, exc))

def _import_output_functions(pkgname="outputs"):
    """Make read functions available at module level.
    Functions are imported here if:
        - they are defined in a module toto.input.{modname}
        - they are named as read_{modname}
    """
    import os
    import sys
    import glob
    from importlib import import_module

    here = os.path.dirname(os.path.abspath(__file__))
    for filename in glob.glob1(os.path.join(here, pkgname), "*.py"):
        module = os.path.splitext(filename)[0]
        if module == "__init__":
            continue
        func_name = "read_{}".format(module)
        try:
            # globals()[func_name] = getattr(
            #     import_module("toto.{}.{}".format(pkgname, module)), func_name
            # )
            import_module("toto.{}.{}".format(pkgname, module))
        except Exception as exc:
            print("Cannot import ouputs function {}:\n{}".format(func_name, exc))


_import_read_functions()
_import_output_functions()
