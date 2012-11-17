import warnings
import functools


def saveit(func):
    """A decorator that caches the return value of a function"""

    name = '_' + func.__name__
    def _wrapper(self, *args, **kwds):
        if not hasattr(self, name):
            setattr(self, name, func(self, *args, **kwds))
        return getattr(self, name)
    return _wrapper

cacheit = saveit

def prevent_recursion(default):
    """A decorator that returns the return value of `default` in recursions"""
    def decorator(func):
        name = '_calling_%s_' % func.__name__
        def newfunc(self, *args, **kwds):
            if getattr(self, name, False):
                return default()
            setattr(self, name, True)
            try:
                return func(self, *args, **kwds)
            finally:
                setattr(self, name, False)
        return newfunc
    return decorator


def ignore_exception(exception_class):
    """A decorator that ignores `exception_class` exceptions"""
    def _decorator(func):
        def newfunc(*args, **kwds):
            try:
                return func(*args, **kwds)
            except exception_class:
                pass
        return newfunc
    return _decorator


def deprecated(message=None):
    """A decorator for deprecated functions"""
    def _decorator(func, message=message):
        if message is None:
            message = '%s is deprecated' % func.__name__
        def newfunc(*args, **kwds):
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwds)
        return newfunc
    return _decorator


def cached(count):
    """A caching decorator based on parameter objects"""
    def decorator(func):
        return _Cached(func, count)
    return decorator


def weight_cache(func):
    """
    Cache the results of the function if the same positional arguments
    are provided.

    We only cache 1MB, after that we should perform FIFO queries until the size
    of the dict is lower than 1MB
    """

    cache = list()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for rex in cache:
            if args == rex[0]:
                return rex[1]

        result = func(*args, **kwargs)
        cache.append((args, result))

        while cache.__sizeof__() >= 1048576:  # 1MB in bytes
            cache.pop(0)

        return result

    return wrapper


class _Cached(object):

    def __init__(self, func, count):
        self.func = func
        self.cache = []
        self.count = count

    def __call__(self, *args, **kwds):
        key = (args, kwds)
        for cached_key, cached_result in self.cache:
            if cached_key == key:
                return cached_result
        result = self.func(*args, **kwds)
        self.cache.append((key, result))
        if len(self.cache) > self.count:
            del self.cache[0]
        return result
