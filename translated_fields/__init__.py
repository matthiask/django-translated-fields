VERSION = (0, 6, 0)
__version__ = ".".join(map(str, VERSION))

try:
    from .admin import *  # noqa
    from .fields import *  # noqa
except ImportError:  # pragma: no cover
    pass
