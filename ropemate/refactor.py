#!/usr/bin/env python
import os, sys, glob
import urllib, re

bundle_lib_path = os.environ['TM_BUNDLE_SUPPORT'] + '/lib'
sys.path.insert(0, bundle_lib_path)

import rope
from rope.base import libutils
from rope.contrib import codeassist, autoimport
from rope.refactor.extract import ExtractMethod
from rope.refactor.importutils import ImportOrganizer
from rope.refactor.rename import Rename
from rope.refactor.localtofield import LocalToField

import ropemate
from ropemate.utils import *

def autocomplete():
    """Can auto complete your code."""
    with ropemate.context as context:
        offset = caret_position(context.input)
        pid = os.fork()
        result = ""
        if pid == 0:
            try:
                raw_proposals = codeassist.code_assist(context.project, context.input, offset, context.resource)
                sorted_proposals = codeassist.sorted_proposals(raw_proposals)
                proposals = filter(lambda p: p.name != "self=", sorted_proposals)
                if len(proposals) == 0:
                    proposals, errors = simple_module_completion()
                if len(proposals) == 0:
                    tooltip("No completions found!%s" % errors)
                else:
                    completion_popup(proposals)
            except Exception, e:
                tooltip(e)
        return result

def simple_module_completion():
    """tries a simple hack (import+dir()) to help completion of imported c-modules"""
    result = []
    try:
        name = identifier_before_dot()

        if not name:
            return [], " Not at an identifier."
        module = None
        try:
            module = __import__(name)
        except ImportError, e:
            return [], " %s." % e
        
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
        
        # if module is a package, check the direc tory
        if hasattr(module,"__path__"):
          in_dir_names = [os.path.split(n)[1] for n in glob.glob(os.path.join(module.__path__[0], "*"))]
          in_dir_names = [n.replace(".py","") for n in in_dir_names
                              if not n.endswith(".pyc") and not n == "__init__.py"]
          for n in in_dir_names:
              result.append(rope.contrib.codeassist.CompletionProposal(
                      n, None, rope.base.pynames.UnboundName()))
    except Exception, e:
        return [], e
    
    return result, None

def extract_method():
    with ropemate.context as context:
        try:
            offset_length = len(os.environ.get('TM_SELECTED_TEXT', ''))
            if offset_length == 0:
                tooltip("You have to selected some code to extract it as a method")
                return context.input
            offset = caret_position(context.input)-offset_length
            extractor = ExtractMethod(context.project, context.resource, offset, offset+offset_length)
            
            func_name = get_input("Extracted method's name")
            if func_name is None:
                tooltip("Enter a name for the extraced function!")
                return context.input
            changes = extractor.get_changes(func_name)
            result = changes.changes[0].new_contents
        except Exception, e:
            tooltip(e)
            return context.input
        
        return result

def rename():
    with ropemate.context as context:
        if current_identifier() == "":
            tooltip("Select an identifier to rename")
            return context.input
        
        offset = caret_position(context.input)
        try:
            rename = Rename(context.project, context.resource, offset)
            
            func_name = get_input(title="New name",default=rename.old_name)
            if func_name is None or func_name == rename.old_name:
                tooltip("Enter a new name!")
                return context.input
            changes = rename.get_changes(func_name, in_hierarchy=True)
            # remove the current file from the changeset.
            # we will apply the changes to this file manually,
            # (as the result of the TM Command) to keep TM's undo history in order
            current_file_changes = filter_changes_in_current_file(changes,context.resource)
            result = current_file_changes.new_contents
            # apply changes to all other files
            
            context.project.do(changes)
        except Exception, e:
            tooltip(e)
            result = context.input
        
        return result

def goto_definition():
    with ropemate.context as context:
        offset = caret_position(context.input)
        found_resource, line = None, None
        try:
            found_resource, line = codeassist.get_definition_location(
                context.project, context.input, offset, context.resource)
        except rope.base.exceptions.BadIdentifierError, e:
            # fail silently -> the user selected empty space etc
            pass
        except Exception, e:
            tooltip(e)
        
        if found_resource is not None:
            return 'txmt://open?url=file://%s&line=%d' % (
                    urllib.quote(found_resource.real_path), line)
        elif line is not None:
            return 'txmt://open?line=%d' % line
        return ''

def filter_changes_in_current_file(changes,resource):
    change_for_current_file = [f for f in changes.changes
                                if f.resource == resource][0]
    changes.changes.remove(change_for_current_file)
    return change_for_current_file

def organize_imports():
    with ropemate.context as context:
        result = context.input
        try:
            organizer = ImportOrganizer(context.project)
            
            operations = [organizer.organize_imports,
                        organizer.handle_long_imports,
                        organizer.expand_star_imports]
            # haven't found a way to easily combine the changes in-memory
            # so i commit all of them and then return the changed file's content
            for op in operations:
                change = op(context.resource)
                if change:
                    context.project.do(change)
            
            with open(context.resource.real_path, "r") as f:
                result = f.read()
        except Exception, e:
            tooltip(e)
        return result

def complete_import(project, resource, code, offset):
    class ImportProposal(object):
        def __init__(self, name, module):
            self.name = name
            self.display = name + " - " + module
            self.insert = module+"."+name
            self.module = module
            self.type = 'module'
    
    importer = autoimport.AutoImport(project=project, observe=False)
    # find all files with changes and index them again
    for filename in find_unindexed_files(project._address):
        importer.update_resource(libutils.path_to_resource(project, filename))
    
    proposals = importer.import_assist(starting=current_identifier())
    
    if len(proposals) == 0:
        return []
    else:
        return [ImportProposal(p[0], p[1]) for p in proposals]

def find_imports():
    def find_last_import_line(lines):
        x = -1
        for i in range(len(lines)):
            l = lines[i]
            if l.startswith("from") or l.startswith("import"):
                x = i
        return x

    def correct_pacakges(proposals, context):
        for p in proposals:
            path = context.resource.path.split("/")
            module = p.module.split(".")
            idx = 0
            while True:
                if path[idx] != module[idx]:break
                idx += 1
            p.module = ".".join(module[idx:])
    
    with ropemate.context as context:
        offset = caret_position(context.input)
        pid = os.fork()
        result = ""
        if pid == 0:
            try:
                proposals = complete_import(context.project, context.resource, context.input, offset)
                correct_pacakges(proposals, context)
                if len(proposals) == 0:
                    #tooltip("No completions found!")
                    return context.input
                else:
                    register_completion_images()
                    command = TM_DIALOG2+" popup"
                    word = current_identifier()
                    if word:
                        command += " --alreadyTyped "+word
                    command += " --returnChoice"
                    options = [dict([['display',p.display],
                                    ['image', p.type if p.type else "None"],
                                    ['match', p.name],
                                    ['module', p.module]])
                                    for p in proposals]
                    
                    out = call_dialog(command, {'suggestions' : options})
                    
                    # from_plist parses only xml-plists, but dialog returns old-style ascii plists
                    try:
                        import_from_mod_name = re.search(r'module = "(.*)";', out).group(1)
                    except:
                        import_from_mod_name = re.search(r'module = (.*);', out).group(1)
                    try:
                        import_name = re.search(r'match = "(.*)";', out).group(1)
                    except:
                        import_name = re.search(r'match = (.*);', out).group(1)
                    
                    typed_len = len(word)
                    code = context.input[:offset-typed_len] + import_name + context.input[offset:]
                    lines = code.split("\n")
                    idx = find_last_import_line(lines)
                    new_line = "from "+import_from_mod_name+" import "+import_name
                    #tooltip("Added \""+new_line+"\"at line "+str(idx+2))
                    lines = lines[:idx+1]+[new_line]+lines[idx+1:]
                    result = "\n".join(lines)
            except Exception, e:
                tooltip(e)
                return context.input
        return result

def local_to_field():
    with ropemate.context as context:
        try:
            offset = caret_position(context.input)
            operation = LocalToField(context.project, context.resource, offset)
            
            changes = operation.get_changes()
            result = changes.changes[0].new_contents
        except Exception, e:
            tooltip(e)
            return context.input
        
        return result

def main():
    operation = {'extract_method'   : extract_method,
                'rename'            : rename,
                'autocomplete'      : autocomplete,
                'goto_definition'   : goto_definition,
                'organize_imports'  : organize_imports,
                'find_imports'      : find_imports,
                'local_to_field'    : local_to_field}\
                .get(sys.argv[1])
    sys.stdout.write(operation())

if __name__ == '__main__':
    main()
