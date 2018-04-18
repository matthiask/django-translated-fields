VERSION = (0, 0, 1)
__version__ = '.'.join(map(str, VERSION))

try:
    from .fields import *  # noqa
except ImportError:
    pass
