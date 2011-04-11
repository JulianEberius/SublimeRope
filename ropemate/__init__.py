import os, sys
import sublime

from rope.base import project,libutils
from ropemate.path import update_python_path
from rope.contrib import autoimport

class ropecontext(object):
    """a context manager to have a rope project context"""

    def __init__(self, view):
        self.view = view
        self.project = None
        self.resource = None
        self.input = ""

    def __enter__(self):
        file_path = self.view.file_name()
        project_dir = self.find_ropeproject(file_path)
        if project_dir:
            self.project = project.Project(project_dir)
            # no use to have auto import for a single file project
            if not os.path.exists("%s/.ropeproject/globalnames" % project_dir):
                importer = autoimport.AutoImport(project=self.project, observe=True)
                importer.generate_cache()
            if os.path.exists("%s/__init__.py" % project_dir):
                sys.path.append(project_dir)
            
        else:
            #create a single-file project (ignoring all other files in the file's folder)
            folder = os.path.dirname(file_path)
            ignored_res = os.listdir(folder)
            ignored_res.remove(os.path.basename(file_path))
            self.project = project.Project(
                ropefolder=None,projectroot=folder, ignored_resources=ignored_res)
        
        self.resource = libutils.path_to_resource(self.project, file_path)
        update_python_path( self.project.prefs.get('python_path', []) )
        self.input = self.view.substr(sublime.Region(0,self.view.size()))
        
        return self
    
    def __exit__(self, type , value , traceback):
        if type is None:
            self.project.close()

    def find_ropeproject(self, file_dir):
        def traverse_upward(look_for, start_at="."):
            print look_for, start_at
            p = os.path.abspath(start_at)

            while True:
                if look_for in os.listdir(p):
                    return p
                new_p =  os.path.abspath(os.path.join(p, ".."))
                if new_p == p:
                    return None
                p = new_p

        return traverse_upward(".ropeproject", start_at=os.path.split(file_dir)[0])