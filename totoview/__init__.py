from __future__ import absolute_import

__all__ = ['show']

# defining main function here, 
def show(*args,**kwargs):
    from totoview.totoview import showApp
    showApp(*args,**kwargs)