import sublime_plugin, sublime
import ropemate
from rope.contrib import codeassist
import rope
import rope.base.default_config

def match(rex, str):
    m = rex.match(str)
    if m:
        return m.group(0)
    else:
        return None

class PythonCompletions(sublime_plugin.EventListener):

    def on_query_completions(self, view, prefix, locations):
        # Only trigger within HTML
        if not view.match_selector(locations[0], "source.python"):
            return []
        with ropemate.ropecontext(view) as context:
            raw_proposals = codeassist.code_assist(context.project, context.input, locations[0], context.resource)
            sorted_proposals = codeassist.sorted_proposals(raw_proposals)
            proposals = filter(lambda p: p.name != "self=", sorted_proposals)
            if len(proposals) == 0:
                proposals, errors = self.simple_module_completion()
        return [(str(p),p.name) for p in proposals]

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

