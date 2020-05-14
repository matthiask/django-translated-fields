VERSION = (0, 9, 0)
__version__ = ".".join(map(str, VERSION))

try:
    import django
except ModuleNotFoundError:  # pragma: no cover
    pass
else:
    from .admin import *  # noqa
    from .fields import *  # noqa
    from .utils import *  # noqa
