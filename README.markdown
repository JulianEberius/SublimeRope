**SublimeRope**
===========================

Integrates the Python refactoring/completion framework Rope with Sublime Text 2.
For now, it adds Rope completions to the ST2 completion menu, and adds a command goto_python_definition. It is a port of RopeMate, which I wrote for TextMate, and does not yet include all the features of RopeMate (or Rope for that matter).

I have only tested it on the latest dev build (2045) on OSX and Ubuntu so far.

Copyright (C) 2010 Julian Eberius

USAGE
-----

Just unzip / git clone the folder SublimeRope into ST2's Packages folder.

*IMPORTANT*: Since ST2 for the moment has no API to find or mark the project root folder, you have to mark your project's root manually, so that Rope knows which folders to scan for completions / definitions.

Just create a folder named ".ropeproject" at the root of your project (Rope would do that anyway when a project is initialized). 

    cd /path/to/your/project
    mkdir .ropeproject

Then edit any file in this folder or its subfolders and you should get completions, and goto_python_definition should work. Of course, you need to set a key binding, e.g., add this to your user keybindings:

    { "keys": ["super+f3"], "command": "goto_python_definition"}

If you are using virtualenv for your project, add the path to the virtualenv in .ropeproject/config.py (there should be a commented-out line already in the file in set_prefs).

    prefs.add('python_path', '/Users/ebi/dev/project/lib/python2.7/site-packages/')

License: 
--------

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

Have a look at "LICENSE.txt" file for more information.

EXTERNAL LICENSES
-----------------
This project uses code from other open source projects (Rope) 
which may include licenses of their own.
