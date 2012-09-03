import sublime_plugin
import sublime
import threading
import sys
import os
import glob
import re
import ast

# always import the bundled rope
path = os.path.dirname(os.path.normpath(os.path.abspath(__file__)))
sys.path.insert(0, path)

import rope
import ropemate
from rope.contrib import codeassist
from rope.refactor.rename import Rename
from rope.refactor.extract import ExtractMethod, ExtractVariable
from rope.refactor.inline import InlineVariable
from rope.refactor.restructure import Restructure
from rope.base.exceptions import ModuleSyntaxError
from rope.base.taskhandle import TaskHandle
from rope.base.pycore import ModuleNotFoundError


class PythonEventListener(sublime_plugin.EventListener):
    '''Updates Rope's database in response to events (e.g. post_save)'''
    def on_post_save(self, view):
        if not "Python" in view.settings().get('syntax'):
            return
        with ropemate.context_for(view) as context:
            context.importer.generate_cache(
                resources=[context.resource])

def get_setting(key, default_value=None):
    try:
        settings = sublime.active_window().active_view().settings()
        if settings.has('rope_{0}'.format(key)):
            return settings.get('rope_{0}'.format(key))
    except:
        pass
    s = sublime.load_settings('SublimeRope.sublime-settings')
    return s.get(key, default_value)

class PythonCompletions(sublime_plugin.EventListener):
    ''''Provides rope completions for the ST2 completion system.'''
    def __init__(self):
        s = sublime.load_settings("SublimeRope.sublime-settings")
        s.add_on_change("suppress_word_completions", self.load_settings)
        s.add_on_change("suppress_explicit_completions", self.load_settings)
        s.add_on_change("use_simple_completion", self.load_settings)
        s.add_on_change("add_parameter_snippet", self.load_settings)
        self.load_settings(s)

    def load_settings(self, settings=None):
        if not settings:
            settings = sublime.load_settings("SublimeRope.sublime-settings")
        self.suppress_word_completions = settings.get(
            "suppress_word_completions")
        self.suppress_explicit_completions = settings.get(
            "suppress_explicit_completions")
        self.use_simple_completion = settings.get(
            "use_simple_completion")
        self.add_parameter_snippet = settings.get(
            "add_parameter_snippet")

    def proposal_string(self, p):
        if p.parameters:
            params = [par for par in p.parameters if par != "self"]
            result = p.name + "("
            result += ", ".join(param for param in params)
            result += ")"
        else:
            result = p.name
        result += "\t(%s, %s)" % (p.scope, p.type)
        return result

    def insert_string(self, p):
        if p.parameters and not p.from_X_import:
            params = [par for par in p.parameters if par != "self"]
            result = p.name + "("
            if self.add_parameter_snippet:
                result += ", ".join("${%i:%s}" % (idx+1, param) for idx, param in enumerate(params)) + ")"
            else:
                if len(params) == 0:
                    result += ")"
                else:
                    result += "$1)"
        else:
            result = p.name
        return result

    def on_query_completions(self, view, prefix, locations):
        if not view.match_selector(locations[0], "source.python"):
            return []

        with ropemate.context_for(view) as context:
            loc = locations[0]
            try:
                raw_proposals = codeassist.code_assist(
                    context.project, context.input, loc, context.resource,
                    maxfixes=3, later_locals=False)
            except ModuleSyntaxError:
                raw_proposals = []
            if len(raw_proposals) <= 0 and self.use_simple_completion:
                # try the simple hackish completion
                line = view.substr(view.line(loc))
                identifier = line[:view.rowcol(loc)[1]].strip(' .')
                if ' ' in identifier:
                    identifier = identifier.split(' ')[-1]
                raw_proposals = self.simple_module_completion(view, identifier)

        proposals = codeassist.sorted_proposals(raw_proposals)

        proposals = [
            (self.proposal_string(p), self.insert_string(p))
            for p in proposals if p.name != 'self='
        ]

        completion_flags = 0
        if self.suppress_word_completions:
            completion_flags = sublime.INHIBIT_WORD_COMPLETIONS

        if self.suppress_explicit_completions:
            completion_flags |= sublime.INHIBIT_EXPLICIT_COMPLETIONS

        return (proposals, completion_flags)

    def simple_module_completion(self, view, identifier):
        """tries a simple hack (import+dir()) to help
        completion of imported c-modules"""
        result = []

        path_added = None
        filename = view.file_name()
        if filename is not None:
            # Not an unsaved buffer, take its path into account.
            path_added = os.path.split(filename)[0]
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
            if path_added is not None:
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
                    n, "imported", rope.base.pynames.UnboundName()))
            return result
        return None


class PythonGetDocumentation(sublime_plugin.TextCommand):
    '''Retrieves the docstring for the identifier under the cursor and
    displays it in a new panel.'''
    def run(self, edit):
        view = self.view
        row, col = view.rowcol(view.sel()[0].a)
        offset = view.text_point(row, col)
        if view.substr(offset) in [u'(', u')']:
            offset = view.text_point(row, col - 1)
        with ropemate.context_for(view) as context:
            try:
                doc = codeassist.get_doc(
                    context.project, context.input, offset, context.resource,
                    maxfixes=3)
                if not doc:
                    raise rope.base.exceptions.BadIdentifierError
                self.output(doc)
            except rope.base.exceptions.BadIdentifierError:
                word = self.view.substr(self.view.word(offset))
                self.view.set_status(
                    "rope_documentation_error",
                    "No documentation found for %s" % word
                )

                def clear_status_callback():
                    self.view.erase_status("rope_documentation_error")
                sublime.set_timeout(clear_status_callback, 5000)

    def output(self, string):
        out_view = self.view.window().get_output_panel(
            "rope_python_documentation"
        )
        r = sublime.Region(0, out_view.size())
        e = out_view.begin_edit()
        out_view.erase(e, r)
        out_view.insert(e, 0, string)
        out_view.end_edit(e)
        out_view.show(0)
        self.view.window().run_command(
            "show_panel", {"panel": "output.rope_python_documentation"})


class PythonJumpToGlobal(sublime_plugin.TextCommand):
    """Allows the user to select from a list of all known globals
    in a quick panel to jump there."""
    def run(self, edit):
        with ropemate.context_for(self.view) as context:
            self.names = list(context.importer.get_all_names())
            self.view.window().show_quick_panel(
                self.names, self.on_select_global, sublime.MONOSPACE_FONT)

    def on_select_global(self, choice):
        def loc_to_str(loc):
            resource, line = loc
            return "%s:%s" % (resource.path, line)

        if choice is not -1:
            selected_global = self.names[choice]
            with ropemate.context_for(self.view) as context:
                self.locs = context.importer.get_name_locations(selected_global)
                self.locs = map(loc_to_str, self.locs)

                if not self.locs:
                    return
                if len(self.locs) == 1:
                    self.on_select_location(0)
                else:
                    self.view.window().show_quick_panel(
                        self.locs,
                        self.on_select_location,
                        sublime.MONOSPACE_FONT
                    )

    def on_select_location(self, choice):
        loc = self.locs[choice]
        with ropemate.context_for(self.view) as context:
            path, line = loc.split(":")
            path = context.project._get_resource_path(path)
            self.view.window().open_file(
                "%s:%s" % (path, line),
                sublime.ENCODED_POSITION
            )


class PythonAutoImport(sublime_plugin.TextCommand):
    """Provides a list of project globals starting with the
    word under the cursor"""
    def run(self, edit):
        view = self.view
        row, col = view.rowcol(view.sel()[0].a)
        self.offset = view.text_point(row, col)
        with ropemate.context_for(view) as context:
            word = self.view.substr(self.view.word(self.offset))
            self.candidates = list(context.importer.import_assist(word))
            self.view.window().show_quick_panel(
                map(lambda c: [c[0], c[1]], self.candidates),
                self.on_select_global, sublime.MONOSPACE_FONT)

    def on_select_global(self, choice):
        if choice is not -1:
            name, module = self.candidates[choice]
            with ropemate.context_for(self.view) as context:
                # check whether adding an import is necessary, and where
                all_lines = self.view.lines(
                    sublime.Region(0, self.view.size())
                )
                line_no = context.importer.find_insertion_line(context.input)
                insert_import_str = "from %s import %s\n" % (module, name)
                existing_imports_str = self.view.substr(
                    sublime.Region(all_lines[0].a, all_lines[line_no - 1].b))
                do_insert_import = \
                    insert_import_str not in existing_imports_str
                insert_import_point = all_lines[line_no].a

                # the word prefix that is replaced
                original_word = self.view.word(self.offset)

                # replace the prefix, add the import if necessary
                e = self.view.begin_edit()
                self.view.replace(e, original_word, name)
                if do_insert_import:
                    self.view.insert(
                        e, insert_import_point, insert_import_str)
                self.view.end_edit(e)


class AbstractPythonRefactoring(object):
    '''Some common functionality for the rope refactorings.
    Implement __init__, default_input, get_changes and
    create_refactoring_operation in the subclasses to add a new refactoring.'''
    def __init__(self, message):
        self.message = message

    def run(self, edit, block=False):
        self.view.run_command("save")
        self.original_loc = self.view.rowcol(self.view.sel()[0].a)
        with ropemate.context_for(self.view) as context:
            self.sel = self.view.sel()[0]

            self.refactoring = self.create_refactoring_operation(
                context.project, context.resource, self.sel.a, self.sel.b)
            self.view.window().show_input_panel(
                self.message,
                self.default_input(),
                self.input_callback,
                None,
                None
            )

    def input_callback(self, input_str):
        with ropemate.context_for(self.view) as context:
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
            self.view.window().open_file(path, sublime.ENCODED_POSITION)

    def default_input(self):
        raise NotImplemented

    def get_changes(self, input_str):
        raise NotImplemented

    def create_refactoring_operation(self, project, resource, start, end):
        raise NotImplemented


class PythonRefactorRename(AbstractPythonRefactoring,
    sublime_plugin.TextCommand):
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


class PythonRefactorExtractMethod(AbstractPythonRefactoring,
    sublime_plugin.TextCommand):
    '''Creates a new function or method (depending on the context) from the
    selected lines'''
    def __init__(self, *args, **kwargs):
        AbstractPythonRefactoring.__init__(self, message="New method name")
        sublime_plugin.TextCommand.__init__(self, *args, **kwargs)

    def default_input(self):
        return "new_method"

    def get_changes(self, input_str):
        return self.refactoring.get_changes(input_str)

    def create_refactoring_operation(self, project, resource, start, end):
        return ExtractMethod(project, resource, start, end)


class PythonRefactorExtractVariable(AbstractPythonRefactoring,
    sublime_plugin.TextCommand):
    '''Creates a new variable from the selected lines'''
    def __init__(self, *args, **kwargs):
        AbstractPythonRefactoring.__init__(self, message="New variable name")
        sublime_plugin.TextCommand.__init__(self, *args, **kwargs)

    def default_input(self):
        return "new_variable"

    def get_changes(self, input_str):
        return self.refactoring.get_changes(input_str)

    def create_refactoring_operation(self, project, resource, start, end):
        return ExtractVariable(project, resource, start, end)


class PythonRefactorInlineVariable(AbstractPythonRefactoring,
    sublime_plugin.TextCommand):
    '''Inline the current variable'''
    def __init__(self, *args, **kwargs):
        AbstractPythonRefactoring.__init__(self,
            message='Inline all occurred?'
        )
        sublime_plugin.TextCommand.__init__(self, *args, **kwargs)

    def default_input(self):
        return "yes"

    def input_callback(self, input_str):
        if input_str in ('no', 'n'):
            only_current = True
        elif input_str in ('yes', 'y'):
            only_current = False
        else:
            return
        return AbstractPythonRefactoring.input_callback(self, only_current)

    def get_changes(self, only_current):
        return self.refactoring.get_changes(remove=(not only_current),
                                            only_current=only_current)

    def create_refactoring_operation(self, project, resource, start, end):
        return InlineVariable(project, resource, start)


class PythonRefactorRestructure(sublime_plugin.TextCommand):
    '''Reestruture coincidences'''

    def run(self, edit, block=False):
        self.messages = ['Pattern', 'Goal', 'Args']
        self.defaults = ["${}", "${}", "{'': 'name='}"]
        self.args = []

        self.view.run_command("save")
        self.original_loc = self.view.rowcol(self.view.sel()[0].a)
        self._window = self.view.window()
        self._window.show_input_panel(
            self.messages[0], self.defaults[0], self.get_goal,
            None, None
        )

    def get_goal(self, input_str):
        if input_str in self.defaults:
            sublime.status_message('You have to provide a valid pattern for this'
                ' restructure. Cancelling...')
            return

        self.args.append(str(input_str))
        self._window.show_input_panel(
            self.messages[1], self.defaults[1], self.get_args,
            None, None
        )

    def get_args(self, input_str):
        if input_str in self.defaults:
            sublime.status_message('You have to provide valid arguments for this'
                ' restructure. Cancelling...')
            return

        self.args.append(str(input_str))
        self._window.show_input_panel(
            self.messages[2], self.defaults[2], self.process_args,
            None, None
        )

    def process_args(self, input_str):
        if input_str in self.defaults:
            sublime.status_message('You have to provide valid arguments for this'
                ' restructure. Cancelling...')
            return

        try:
            self.args.append(ast.literal_eval(input_str))
        except:
            sublime.error_message("Malformed string detected in Args.\n\n"
                "The Args value must be a Python dictionary")
            return

        with ropemate.context_for(self.view) as context:
            self.refactoring = Restructure(
                context.project, self.args[0], self.args[1], self.args[2])

            self.changes = self.refactoring.get_changes()

            try:
                context.project.do(self.changes)
                sublime.error_message(self.changes.get_description())
            except ModuleNotFoundError, e:
                sublime.error_message(e)


class GotoPythonDefinition(sublime_plugin.TextCommand):
    '''
    Shows the definition of the identifier under the cursor, project-wide.
    '''
    def run(self, edit, block=False):
        with ropemate.context_for(self.view) as context:
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


class PythonGenerateModulesCache(sublime_plugin.TextCommand):
    '''Generate moduls cache used for auto-import and jump-to-globals.
    Uses `generate_modules_cache` in a thread in order to build the cache'''

    class GenerateModulesCache(threading.Thread):
        def __init__(self, ctx, modules):
            self.ctx = ctx
            self.modules = modules
            threading.Thread.__init__(self)

        def run(self):
            self.ctx.importer.generate_modules_cache(self.modules)
            self.ctx.__exit__(None, None, None)
            self.ctx.building = False

    def run(self, edit):
        modules = get_setting('autoimport_modules', [])
        if modules:
            sublime.status_message('Generating modules cache {0}...'.format(
                ' '.join(modules)
            ))
            ctx = ropemate.context_for(self.view)
            ctx.building = True
            ctx.__enter__()
            thread = PythonGenerateModulesCache.GenerateModulesCache(ctx,
                                                                    modules)
            thread.start()
        else:
            sublime.error_message("Missing modules in configuration file")


class PythonRegenerateCache(sublime_plugin.TextCommand):
    '''Regenerates the cache used for jump-to-globals and auto-imports.
    It is regenerated partially on every save, but sometimes a full regenerate
    might be neceessary.'''

    class RegenerateCacheThread(threading.Thread):
        def __init__(self, ctx):
            self.ctx = ctx
            threading.Thread.__init__(self)

        def run(self):
            self.ctx.importer.clear_cache()
            self.ctx.build_cache()
            self.ctx.__exit__(None, None, None)
            self.ctx.building = False

    def run(self, edit):
        ctx = ropemate.context_for(self.view)
        ctx.building = True
        # we have to enter on main, but build on worker thread
        ctx.__enter__()
        thread = PythonRegenerateCache.RegenerateCacheThread(ctx)
        thread.start()


class RopeNewProject(sublime_plugin.WindowCommand):
    '''Asks the user for project- and virtualenv directory and creates a
    configured rpe project with these values'''
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
            virtualenv = self._find_virtualenv(path)
            if not virtualenv:
                return
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
            self.window.active_view().run_command("python_regenerate_cache")
        except Exception, e:
            msg = "Could not create project folder at %s.\nException: %s"
            sublime.error_message(msg % (self.proj_dir, str(e)))
            return

    def _find_virtualenv(self, path):
        if sublime.platform() == "windows":
            site_p_dir = glob.glob(
                os.path.join(path, "Lib", "site-packages"))
            error = '''Did not find a virtualenv at %s.
Looking for path matching %s/Lib/site-packages'''
        else:  # "linux", "osx"
            cwd = os.getcwd()
            os.chdir(self.proj_dir)
            site_p_dir = glob.glob(
                os.path.join(path, "lib", "python*", "site-packages"))
            os.chdir(cwd)
            error = '''Did not find a virtualenv at %s.
Looking for path matching %s/lib/python*/site-packages'''

        if not len(site_p_dir) == 1:
            sublime.error_message(error % (path, path))
            virtualenv = None
        else:
            virtualenv = site_p_dir[0]
        return virtualenv
