# flake8: noqa

__version__ = "0"
__author__ = "Daniel Jones <http://www.erase.net/>"

from .core import *
from .oscillator import *
from .scalar import *
from .sequence import *
from .chance import *
from .lsystem import *
from .markov import *
from .warp import *
from .static import *
from .tonal import *
from .fade import *

__all__ = []
key = value = None
for key, value in vars().items():
    try:
        # Add every class to pydoc
        if issubclass(value, object):
            __all__.append(key)
    except TypeError:
        pass
