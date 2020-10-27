from __future__ import absolute_import

__all__ = ['show']
__version__='0.0.1'
# defining main function here, 
def show(*args,**kwargs):
    from totoview.totoview import showApp
    showApp(*args,**kwargs)