VERSION = (0, 11, 3)
__version__ = ".".join(map(str, VERSION))

try:
    import django  # noqa
except ModuleNotFoundError:  # pragma: no cover
    pass
else:
    from .admin import *  # noqa
    from .fields import *  # noqa
    from .utils import *  # noqa
