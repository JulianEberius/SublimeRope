import os
import sys

from rope.base import utils


std_lib_path = None


def _stdlib_path():
    if not std_lib_path:
        global std_lib_path
        try:
            import distutils.sysconfig
            std_lib_path = distutils.sysconfig.get_python_lib(standard_lib=True)
        except (IOError, ImportError):
            # original code from older versions of rope is used when
            # distutil is not installed
            import inspect
            std_lib_path = os.path.dirname(inspect.getsourcefile(inspect))
    return std_lib_path


@utils.cached(1)
def standard_modules():
    return python_modules() | dynload_modules()


@utils.cached(1)
def python_modules():
    result = set()
    lib_path = _stdlib_path()
    if not lib_path.endswith('.zip') and os.path.exists(lib_path):
        for name in os.listdir(lib_path):
            path = os.path.join(lib_path, name)
            if os.path.isdir(path):
                if '-' not in name:
                    result.add(name)
            else:
                if name.endswith('.py'):
                    result.add(name[:-3])
    return result


@utils.cached(1)
def dynload_modules():
    result = set(sys.builtin_module_names)
    dynload_path = os.path.join(_stdlib_path(), 'lib-dynload')
    if os.path.exists(dynload_path):
        for name in os.listdir(dynload_path):
            path = os.path.join(dynload_path, name)
            if os.path.isfile(path):
                if name.endswith('.so') or name.endswith('.dll'):
                    result.add(os.path.splitext(name)[0])
    return result
