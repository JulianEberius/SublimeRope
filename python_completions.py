import sublime_plugin
import sublime
import ropemate
from rope.contrib import codeassist
from rope.refactor.rename import Rename
import rope
import os
import glob
import sys
import re
from rope.base.exceptions import ModuleSyntaxError
from rope.base.taskhandle import TaskHandle


class PythonGetDocumentation(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        row, col = view.rowcol(view.sel()[0].a)
        offset = view.text_point(row, col)
        with ropemate.ropecontext(view) as context:
            try:
                doc = codeassist.get_doc(
                    context.project, context.input, offset, context.resource)
                self.output(doc)
            except rope.base.exceptions.BadIdentifierError:
                word = self.view.substr(self.view.word(offset))
                self.view.set_status(
                    "rope_documentation_error", "No documentation found for %s" % word)

                def clear_status_callback():
                    self.view.erase_status("rope_documentation_error")
                sublime.set_timeout(clear_status_callback, 5000)

    def output(self, string):
        out_view = self.view.window().get_output_panel("rope_python_documentation")
        r = sublime.Region(0, out_view.size())
        e = out_view.begin_edit()
        out_view.erase(e, r)
        out_view.insert(e, 0, string)
        out_view.end_edit(e)
        out_view.show(0)
        self.view.window().run_command(
            "show_panel", {"panel": "output.rope_python_documentation"})
        self.view.window().focus_view(out_view)


class PythonCompletions(sublime_plugin.EventListener):

    def on_query_completions(self, view, prefix, locations):
        if not view.match_selector(locations[0], "source.python"):
            return []

        loc = locations[0]
        line = view.substr(view.line(loc))

        with ropemate.ropecontext(view) as context:
            try:
                raw_proposals = codeassist.code_assist(
                    context.project, context.input, loc, context.resource)
            except ModuleSyntaxError:
                raw_proposals = []
            if len(raw_proposals) > 0:
                sorted_proposals = codeassist.sorted_proposals(raw_proposals)
            else:
                # try the simple hackish completion
                identifier = line[:view.rowcol(loc)[1] - 1].strip()
                raw_proposals = self.simple_module_completion(view, identifier)
                sorted_proposals = sorted(raw_proposals, key=lambda x: x.name)

        proposals = filter(lambda p: p.name != "self=", sorted_proposals)
        return [(str(p), p.name) for p in proposals]

    def simple_module_completion(self, view, identifier):
        """tries a simple hack (import+dir()) to help
        completion of imported c-modules"""
        result = []
        return result

        path_added = os.path.split(view.file_name())[0]
        sys.path.insert(0, path_added)

        try:
            if not identifier:
                return []
            module = None
            try:
                module = __import__(identifier)
            except ImportError, e:
                print e, "PATH: ", sys.path
                return []

            names = dir(module)
            for name in names:
                if not name.startswith("__"):
                    p = rope.contrib.codeassist.CompletionProposal(
                        name, "imported", rope.base.pynames.UnboundName())
                    type_name = type(getattr(module, name)).__name__
                    if type_name.find('function') != -1\
                            or type_name.find('method') != -1:
                        p.type = 'function'
                    elif type_name == 'module':
                        p.type = 'module'
                    elif type_name == 'type':
                        p.type = 'class'
                    else:
                        p.type = 'instance'
                    result.append(p)

            # if module is a package, check the directory
            directory_completions = self.add_module_directory_completions(
                module)
            if directory_completions:
                result.extend(directory_completions)
        except Exception, e:
            print e
            return []

        finally:
            sys.path.remove(path_added)

        return result

    def add_module_directory_completions(self, module):
        if hasattr(module, "__path__"):
            result = []
            in_dir_names = [os.path.split(n)[1]
                for n in glob.glob(os.path.join(module.__path__[0], "*"))]
            in_dir_names = set(os.path.splitext(n)[0]
                for n in in_dir_names if "__init__" not in n)
            for n in in_dir_names:
                result.append(rope.contrib.codeassist.CompletionProposal(
                    n, None, rope.base.pynames.UnboundName()))
            return result
        return None


class PythonRefactorRename(sublime_plugin.TextCommand):

    def run(self, edit, block=False):
        self.view.run_command("save")
        with ropemate.ropecontext(self.view) as context:
            self.sel = self.view.sel()[0]
            word = self.view.substr(self.view.word(self.sel.b))

            self.rename = Rename(context.project, context.resource, self.sel.b)
            self.view.window().show_input_panel(
                "New name", word, self.new_name_entered, None, None)

    def new_name_entered(self, new_name):
        with ropemate.ropecontext(self.view) as context:
            if new_name is None or new_name == self.rename.old_name:
                return
            changes = self.rename.get_changes(new_name, in_hierarchy=True)
            self.handle = TaskHandle(name="rename_handle")
            self.handle.add_observer(self.refactoring_done)
            context.project.do(changes, task_handle=self.handle)

    def refactoring_done(self):
        percent_done = self.handle.current_jobset().get_percent_done()
        if percent_done == 100:
            # force reload... does not seem to work
            pass



class GotoPythonDefinition(sublime_plugin.TextCommand):

    def run(self, edit, block=False):
        with ropemate.ropecontext(self.view) as context:
            offset = self.view.sel()[0].a
            found_resource, line = None, None
            try:
                found_resource, line = codeassist.get_definition_location(
                    context.project, context.input, offset, context.resource)
            except rope.base.exceptions.BadIdentifierError, e:
                # fail silently -> the user selected empty space etc
                pass
            except Exception, e:
                print e
            window = sublime.active_window()

            if found_resource is not None:
                path = found_resource.real_path + ":" + str(line)
                window.open_file(path, sublime.ENCODED_POSITION)
            elif line is not None:
                path = self.view.file_name() + ":" + str(line)
                window.open_file(path, sublime.ENCODED_POSITION)


class RopeNewProject(sublime_plugin.WindowCommand):
    def run(self):
        folders = self.window.folders()
        suggested_folder = folders[0] if folders else os.path.expanduser("~")
        self.window.show_input_panel(
            "Enter project root:", suggested_folder, self.entered_proj_dir,
            None, None)

    def entered_proj_dir(self, path):
        if not os.path.isdir(path):
            sublime.error_message("Is not a directory: %s" % path)
            return

        self.proj_dir = path

        # find out virtualenv
        if "WORKON_HOME" in os.environ:
            suggested_folder = os.environ['WORKON_HOME']
        else:
            suggested_folder = ""  # os.path.expanduser("~")
        self.window.show_input_panel(
            "Enter virtualenv dir or leave empty:", suggested_folder,
            self.done, None, None)

    def done(self, path):
        if path == "":
            virtualenv = None
        else:
            path = os.path.expanduser(path)
            site_p_dir = glob.glob(
                os.path.join(path, "lib", "python*", "site-packages"))
            if not len(site_p_dir) == 1:
                error = '''Did not find a virtualenv at %s.
    Looking for path matching %s/lib/python*/site-packages'''
                sublime.error_message(error % (path, path))
                return
            else:
                virtualenv = site_p_dir[0]

        try:
            project = rope.base.project.Project(
                projectroot=self.proj_dir)

            project.close()
            # now setup the project
            if virtualenv:
                conf_py_path = os.path.join(
                    self.proj_dir, ".ropeproject", "config.py")
                with open(conf_py_path) as conf_py:
                    conf_str = conf_py.read()
                conf_str = re.sub(
                    r"#prefs.add\('python_path', '~/python/'\)",
                    "prefs.add('python_path', '%s')" % virtualenv,
                    conf_str)
                with open(conf_py_path, "w") as conf_py:
                    conf_py.write(conf_str)
        except Exception, e:
            msg = "Could not create project folder at %s.\nException: %s"
            sublime.error_message(msg % (self.proj_dir, str(e)))
            return
