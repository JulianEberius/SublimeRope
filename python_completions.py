import sublime_plugin, sublime
import ropemate
from rope.contrib import codeassist
from rope.refactor.rename import Rename
import rope
import rope.base.default_config
import re, os, glob, sys

def match(rex, str):
    m = rex.match(str)
    if m:
        return m.group(0)
    else:
        return None

class PythonCompletions(sublime_plugin.EventListener):

    def on_query_completions(self, view, prefix, locations):
        if not view.match_selector(locations[0], "source.python"):
            return []

        loc = locations[0]
        line = view.substr(view.line(loc))

        match = re.match(r'^from ([A-Za-z_]+) import.*$', line)
        if match:
            identifier = match.group(1)
            raw_proposals = self.simple_module_completion(view, identifier)
            sorted_proposals = sorted(raw_proposals, key=lambda x:x.name)
        else:
            with ropemate.ropecontext(view) as context:
                # sys.path.insert(0,"/Users/ebi/Applications/eclipse/plugins/org.python.pydev.debug_1.6.5.2011020317/pysrc")
                # import pydevd;pydevd.settrace()
                raw_proposals = codeassist.code_assist(context.project, context.input, loc, context.resource)
                if len(raw_proposals) > 0:
                    sorted_proposals = codeassist.sorted_proposals(raw_proposals)
                else:
                    # try the simple hackish completion
                    identifier = line[:view.rowcol(loc)[1]-1].strip()
                    raw_proposals = self.simple_module_completion(view, identifier)
                    sorted_proposals = sorted(raw_proposals, key=lambda x:x.name)

        proposals = filter(lambda p: p.name != "self=", sorted_proposals)
        return [(str(p),p.name) for p in proposals]

    def simple_module_completion(self, view, identifier):
        """tries a simple hack (import+dir()) to help completion of imported c-modules"""
        result = []
        path_added = os.path.split(view.file_name())[0]
        sys.path.insert(0,path_added)

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
                    if type_name.find('function') != -1 or type_name.find('method') != -1:
                        p.type = 'function'
                    elif type_name == 'module':
                        p.type = 'module'
                    elif type_name == 'type':
                        p.type = 'class'
                    else:
                        p.type = 'instance'
                    result.append(p)

            # if module is a package, check the directory
            directory_completions = self.add_module_directory_completions(module)
            if directory_completions:
                result.extend(directory_completions)
        except Exception, e:
            print e
            return []

        finally:
            sys.path.remove(path_added)

        return result

    def add_module_directory_completions(self, module):
        if hasattr(module,"__path__"):
            result = []
            in_dir_names = [os.path.split(n)[1] for n in glob.glob(os.path.join(module.__path__[0], "*"))]
            in_dir_names = set(os.path.splitext(n)[0] for n in in_dir_names if "__init__" not in n)
            for n in in_dir_names:
                result.append(rope.contrib.codeassist.CompletionProposal(
                    n, None, rope.base.pynames.UnboundName()))
            return result
        return None

class PythonRefactorRename(sublime_plugin.TextCommand):

    def run(self, edit, block=False):
        with ropemate.ropecontext(self.view) as context:
            self.sel = self.view.sel()[0]
            word = self.view.substr(self.view.word(self.sel.b))

            self.rename = Rename(context.project, context.resource, self.sel.b)
            self.view.window().show_input_panel("New name", word, self.new_name_entered, None, None)

    def new_name_entered(self, new_name):
        with ropemate.ropecontext(self.view) as context:
            if new_name is None or new_name == self.rename.old_name:
                return

            changes = self.rename.get_changes(new_name, in_hierarchy=True)
            context.project.do(changes)
            self.view.show(self.sel)

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
                path = found_resource.real_path+":"+str(line)
                window.open_file(path,sublime.ENCODED_POSITION)
            elif line is not None:
                path = self.view.file_name()+":"+str(line)
                window.open_file(path,sublime.ENCODED_POSITION)
