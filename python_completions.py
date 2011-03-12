import sublime_plugin, sublime
import ropemate
from rope.contrib import codeassist
import rope
import glob

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

    # def identifier_before_dot(self):
    #     if 'TM_CURRENT_WORD' not in os.environ:
    #         os.environ['TM_CURRENT_WORD'] = os.environ.get('TM_CURRENT_LINE')
        
    #     word = current_word(r"^[\.A-Za-z_0-9]*", direction='left')
    #     if word:
    #         return word[:-1]
    #     return ""

    # def simple_module_completion(self):
    #     """tries a simple hack (import+dir()) to help completion of imported c-modules"""
    #     result = []
    #     try:
    #         name = self.identifier_before_dot()

    #         if not name:
    #             return [], " Not at an identifier."
    #         module = None
    #         try:
    #             module = __import__(name)
    #         except ImportError, e:
    #             return [], " %s." % e
            
    #         names = dir(module)
            
    #         for name in names:
    #             if not name.startswith("__"):
    #                 p = rope.contrib.codeassist.CompletionProposal(
    #                     name, "imported", rope.base.pynames.UnboundName())
    #                 type_name = type(getattr(module, name)).__name__
    #                 if type_name.find('function') != -1 or type_name.find('method') != -1:
    #                     p.type = 'function'
    #                 elif type_name == 'module':
    #                     p.type = 'module'
    #                 elif type_name == 'type':
    #                     p.type = 'class'
    #                 else:
    #                     p.type = 'instance'
    #                 result.append(p)
            
    #         # if module is a package, check the direc tory
    #         if hasattr(module,"__path__"):
    #           in_dir_names = [os.path.split(n)[1] for n in glob.glob(os.path.join(module.__path__[0], "*"))]
    #           in_dir_names = [n.replace(".py","") for n in in_dir_names
    #                               if not n.endswith(".pyc") and not n == "__init__.py"]
    #           for n in in_dir_names:
    #               result.append(rope.contrib.codeassist.CompletionProposal(
    #                       n, None, rope.base.pynames.UnboundName()))
    #     except Exception, e:
    #         return [], e
        
    #     return result, None

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

