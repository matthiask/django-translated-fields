VERSION = (0, 7, 1)
__version__ = ".".join(map(str, VERSION))

try:
    from .admin import *  # noqa
    from .fields import *  # noqa
    from .utils import *  # noqa
except ImportError:  # pragma: no cover
    pass
