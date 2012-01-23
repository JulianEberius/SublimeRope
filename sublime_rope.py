import sublime_plugin
import sublime
import sys
import os
import glob
import re

# always import the bundled rope
path = os.path.dirname(os.path.normpath(os.path.abspath(__file__)))
sys.path.insert(0, path)

import rope
import ropemate
from rope.contrib import codeassist
from rope.refactor.rename import Rename
from rope.refactor.extract import ExtractMethod
from rope.base.exceptions import ModuleSyntaxError
from rope.base.taskhandle import TaskHandle


class PythonEventListener(sublime_plugin.EventListener):
    '''Updates Rope's database in response to events (e.g. post_save)'''
    def on_post_save(self, view):
        with ropemate.ropecontext(view) as context:
            context.importer.generate_cache(
                resources=[context.resource])


class PythonCompletions(sublime_plugin.EventListener):
    ''''Provides rope completions for the ST2 completion system.'''
    def on_query_completions(self, view, prefix, locations):
        if not view.match_selector(locations[0], "source.python"):
            return []

        with ropemate.ropecontext(view) as context:
            loc = locations[0]
            try:
                raw_proposals = codeassist.code_assist(
                    context.project, context.input, loc, context.resource)
            except ModuleSyntaxError:
                raw_proposals = []
            if len(raw_proposals) <= 0:
                # try the simple hackish completion
                line = view.substr(view.line(loc))
                identifier = line[:view.rowcol(loc)[1]].strip(' .')
                if ' ' in identifier:
                    identifier = identifier.split(' ')[-1]
                raw_proposals = self.simple_module_completion(view, identifier)

        sorted_proposals = codeassist.sorted_proposals(raw_proposals)
        proposals = filter(lambda p: p.name != "self=", sorted_proposals)
        return [(str(p), p.name) for p in proposals]

    def simple_module_completion(self, view, identifier):
        """tries a simple hack (import+dir()) to help
        completion of imported c-modules"""
        result = []

        path_added = os.path.split(view.file_name())[0]
        sys.path.insert(0, path_added)

        try:
            if not identifier:
                return []
            module = None
            try:
                module = __import__(identifier)
                if '.' in identifier:
                    module = sys.modules[identifier]
            except ImportError, e:
                # print e, "PATH: ", sys.path
                return []

            names = dir(module)
            for name in names:
                if not name.startswith("__"):
                    p = rope.contrib.codeassist.CompletionProposal(
                        name, "imported", rope.base.pynames.UnboundName())
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
        '''Another simple hack that helps with some packages: add all files in
        a package as completion options'''
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


class PythonGetDocumentation(sublime_plugin.TextCommand):
    '''Retrieves the docstring for the identifier under the cursor and
    displays it in a new panel.'''
    def run(self, edit):
        view = self.view
        row, col = view.rowcol(view.sel()[0].a)
        offset = view.text_point(row, col)
        with ropemate.ropecontext(view) as context:
            try:
                doc = codeassist.get_doc(
                    context.project, context.input, offset, context.resource)
                if not doc:
                    raise rope.base.exceptions.BadIdentifierError
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


class PythonJumpToGlobal(sublime_plugin.TextCommand):
    """Allows the user to select from a list of all known globals
    in a quick panel to jump there."""
    def run(self, edit):
        with ropemate.ropecontext(self.view) as context:
            self.names = list(context.importer.get_all_names())
            self.view.window().show_quick_panel(
                self.names, self.on_select_global, sublime.MONOSPACE_FONT)

    def on_select_global(self, choice):
        def loc_to_str(loc):
            resource, line = loc
            return "%s:%s" % (resource.path, line)

        if choice is not -1:
            selected_global = self.names[choice]
            with ropemate.ropecontext(self.view) as context:
                self.locs = context.importer.get_name_locations(selected_global)
                self.locs = map(loc_to_str, self.locs)

                if not self.locs:
                    return
                if len(self.locs) == 1:
                    self.on_select_location(0)
                else:
                    self.view.window().show_quick_panel(
                        self.locs, self.on_select_location, sublime.MONOSPACE_FONT)

    def on_select_location(self, choice):
        loc = self.locs[choice]
        with ropemate.ropecontext(self.view) as context:
            path, line = loc.split(":")
            path = context.project._get_resource_path(path)
            self.view.window().open_file("%s:%s" % (path, line), sublime.ENCODED_POSITION)


class AbstractPythonRefactoring(object):
    '''Some common functionality for the rope refactorings.
    Implement __init__, default_input, get_changes and create_refactoring_operation
    in the subclasses to add a new refactoring.'''
    def __init__(self, message):
        self.message = message

    def run(self, edit, block=False):
        self.view.run_command("save")
        self.original_loc = self.view.rowcol(self.view.sel()[0].a)
        with ropemate.ropecontext(self.view) as context:
            self.sel = self.view.sel()[0]

            self.refactoring = self.create_refactoring_operation(
                context.project, context.resource, self.sel.a, self.sel.b)
            self.view.window().show_input_panel(
                self.message, self.default_input(), self.input_callback, None, None)

    def input_callback(self, input_str):
        with ropemate.ropecontext(self.view) as context:
            if input_str is None:
                return
            changes = self.get_changes(input_str)
            self.handle = TaskHandle(name="refactoring_handle")
            self.handle.add_observer(self.refactoring_done)
            context.project.do(changes, task_handle=self.handle)

    def refactoring_done(self):
        percent_done = self.handle.current_jobset().get_percent_done()
        if percent_done == 100:
            self.view.run_command('revert')

            row, col = self.original_loc
            path = self.view.file_name() + ":%i:%i" % (row + 1, col + 1)
            self.view.window().open_file(
                path, sublime.ENCODED_POSITION)

    def default_input(self):
        raise NotImplemented

    def get_changes(self, input_str):
        raise NotImplemented

    def create_refactoring_operation(self, project, resource, start, end):
        raise NotImplemented


class PythonRefactorRename(AbstractPythonRefactoring, sublime_plugin.TextCommand):
    '''Renames the identifier under the cursor throughout the project'''
    def __init__(self, *args, **kwargs):
        AbstractPythonRefactoring.__init__(self, message="New name")
        sublime_plugin.TextCommand.__init__(self, *args, **kwargs)

    def input_callback(self, input_str):
        if input_str == self.refactoring.old_name:
            return
        return AbstractPythonRefactoring.input_callback(self, input_str)

    def default_input(self):
        return self.view.substr(self.view.word(self.sel.b))

    def get_changes(self, input_str):
        return self.refactoring.get_changes(input_str, in_hierarchy=True)

    def create_refactoring_operation(self, project, resource, start, end):
        return Rename(project, resource, start)


class PythonRefactorExtractMethod(AbstractPythonRefactoring, sublime_plugin.TextCommand):
    '''Creates a new function or method (depending on the context) from the selected
    lines'''
    def __init__(self, *args, **kwargs):
        AbstractPythonRefactoring.__init__(self, message="New method name")
        sublime_plugin.TextCommand.__init__(self, *args, **kwargs)

    def default_input(self):
        return "new_method"

    def get_changes(self, input_str):
        return self.refactoring.get_changes(input_str)

    def create_refactoring_operation(self, project, resource, start, end):
        return ExtractMethod(project, resource, start, end)


class GotoPythonDefinition(sublime_plugin.TextCommand):
    '''Shows the definition of the identifier under the cursor, project-wide.'''
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


class PythonRegenerateCache(sublime_plugin.TextCommand):
    '''Regenerates the cache used for jump-to-globals and auto-imports.
    It is regenerated partially on every save, but sometimes a full regenerate
    might be neceessary.'''
    def run(self, edit):
        with ropemate.ropecontext(self.view) as context:
            context.importer.clear_cache()
            context.importer.generate_cache()


class RopeNewProject(sublime_plugin.WindowCommand):
    '''Asks the user for project- and virtualenv directory and creates a configured
    rope project with these values'''
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
