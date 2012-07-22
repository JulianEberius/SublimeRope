import os
import sys
import site
import sublime
import tempfile

from rope.base import project, libutils
from rope.base.fscommands import FileSystemCommands
from rope.contrib import autoimport

project_cache = {}


def context_for(view):
    file_path = view.file_name()
    if file_path is None:
        # unsaved buffer
        return RopeContext(view)

    project_dir = _find_ropeproject(file_path)
    if project_dir in project_cache:
        ctx = project_cache[project_dir]
        if ctx.building:
            return RopeContext(view, single_file=True)
        ctx.view = view
        ctx.file_path = view.file_name()
        return ctx
    else:
        ctx = RopeContext(view)
        if project_dir:
            project_cache[project_dir] = ctx
        return ctx


class RopeContext(object):
    """a context manager to have a rope project context"""

    def __init__(self, view, single_file=False):
        self.view = view
        self.project = None
        self.resource = None
        self.tmpfile = None
        self.input = ""
        self.building = False

        self.file_path = self.view.file_name()
        if self.file_path is None:
            # unsaved buffer
            self.file_path = self._create_temp_file()
        self.project_dir = _find_ropeproject(self.file_path)

        if not single_file and self.project_dir:
            self.project = project.Project(self.project_dir, fscommands=FileSystemCommands())
            self.importer = autoimport.AutoImport(
                project=self.project, observe=False)
            if os.path.exists("%s/__init__.py" % self.project_dir):
                sys.path.append(self.project_dir)
        else:
            # create a single-file project(ignoring other files in the folder)
            folder = os.path.dirname(self.file_path)
            ignored_res = os.listdir(folder)
            ignored_res.remove(os.path.basename(self.file_path))

            self.project = project.Project(
                ropefolder=None, projectroot=folder,
                ignored_resources=ignored_res, fscommands=FileSystemCommands())
            self.importer = autoimport.AutoImport(
                project=self.project, observe=False)

    def __enter__(self):
        self.resource = libutils.path_to_resource(self.project, self.file_path)
        _update_python_path(self.project.prefs.get('python_path', []))
        self.input = self.view.substr(sublime.Region(0, self.view.size()))
        return self

    def __exit__(self, type, value, traceback):
        if type is None:
            self.project.close()
        if self.tmpfile is not None:
            os.remove(self.tmpfile.name)

    def build_cache(self):
        key = "building_cache_for_" + self.project.address
        sublime.set_timeout(
            lambda: self.view.set_status(key, "Building Rope cache ..."),
            0)
        self.importer.generate_cache()
        sublime.set_timeout(
            lambda: self.view.erase_status(key),
            0)

    def generate_modules_cache(self, modules):
        key = "generate_modules_cache_for_" + self.project.address
        sublime.set_timeout(
            lambda: self.view.set_status(key, "Building Modules cache ..."),
            0)
        self.importer.generate_modules_cache(modules)
        self.project.sync()
        sublime.set_timeout(
            lambda: self.view.erase_status(key),
            0)

    def _create_temp_file(self):
        self.tmpfile = tempfile.NamedTemporaryFile(delete=False)
        text = self.view.substr(sublime.Region(0, self.view.size()))
        self.tmpfile.write(text)
        self.tmpfile.close()
        return self.tmpfile.name


def _find_ropeproject(file_dir):
    def _traverse_upward(look_for, start_at="."):
        p = os.path.abspath(start_at)

        while True:
            if look_for in os.listdir(p):
                return p
            new_p = os.path.abspath(os.path.join(p, ".."))
            if new_p == p:
                return None
            p = new_p

    return _traverse_upward(
        ".ropeproject", start_at=os.path.split(file_dir)[0])


def _update_python_path(paths):
    "update sys.path and make sure the new items come first"
    old_sys_path_items = list(sys.path)

    for path in paths:
        # see if it is a site dir
        if path.find('site-packages') != -1:
            site.addsitedir(path)
        else:
            sys.path.insert(0, path)

    # Reorder sys.path so new directories at the front.
    new_sys_path_items = set(sys.path) - set(old_sys_path_items)
    sys.path = list(new_sys_path_items) + old_sys_path_items
