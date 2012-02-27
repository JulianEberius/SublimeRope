import os
import sys
import site
import sublime
import tempfile

from rope.base import project, libutils
from rope.base.fscommands import FileSystemCommands
from rope.contrib import autoimport


class RopeContext(object):
    """a context manager to have a rope project context"""

    def __init__(self, view):
        self.view = view
        self.project = None
        self.resource = None
        self.tmpfile = None
        self.input = ""

    def __enter__(self):
        file_path = self.view.file_name()
        if file_path is None:
            # unsaved buffer
            file_path = self._create_temp_file()
        project_dir = self._find_ropeproject(file_path)
        if project_dir:
            self.project = project.Project(project_dir, fscommands=FileSystemCommands())
            self.importer = autoimport.AutoImport(
                project=self.project, observe=True)
            if not os.path.exists("%s/.ropeproject/globalnames" % project_dir):
                # self.importer.generate_cache()
                self.build_cache()
            if os.path.exists("%s/__init__.py" % project_dir):
                sys.path.append(project_dir)
        else:
            # create a single-file project(ignoring other files in the folder)
            folder = os.path.dirname(file_path)
            ignored_res = os.listdir(folder)
            ignored_res.remove(os.path.basename(file_path))

            self.project = project.Project(
                ropefolder=None, projectroot=folder,
                ignored_resources=ignored_res, fscommands=FileSystemCommands())
            self.importer = autoimport.AutoImport(
                project=self.project, observe=True)

        self.resource = libutils.path_to_resource(self.project, file_path)
        _update_python_path(self.project.prefs.get('python_path', []))
        self.input = self.view.substr(sublime.Region(0, self.view.size()))

        return self

    def __exit__(self, type, value, traceback):
        if type is None:
            self.project.close()
        if self.tmpfile is not None:
            os.remove(self.tmpfile.name)

    def build_cache(self):
        # project_files = self.project.pycore.get_python_files()
        # py_path_dirs = self.project.pycore.get_python_path_folders()
        # print map(lambda x: x.real_path, project_files+py_path_dirs)
        # self.importer.generate_cache(project_files + py_path_dirs)
        self.importer.generate_cache()

    def _create_temp_file(self):
        self.tmpfile = tempfile.NamedTemporaryFile(delete=False)
        text = self.view.substr(sublime.Region(0, self.view.size()))
        self.tmpfile.write(text)
        self.tmpfile.close()
        return self.tmpfile.name

    def _find_ropeproject(self, file_dir):
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
