**SublimeRope**
===========================

Integrates the Python refactoring/completion framework Rope with Sublime Text 2.
For now, it adds Rope completions to the ST2 completion menu, and adds a command goto_python_definition. It is a port of RopeMate, which I wrote for TextMate, and does not yet include all the features of RopeMate (or Rope for that matter).

I have tested it on the latest dev build. It seems to work equally well on OSX, Linux and Windows, though I mostly test on OSX.
No guarantees here!

Copyright (C) 2011 Julian Eberius

Basic Usage
-----------

Just unzip / git clone the folder SublimeRope into ST2's Packages folder.

*IMPORTANT*: Since ST2 for the moment has no API to find or mark the project root folder, you have to mark your project's root manually, so that Rope knows which folders to scan for completions / definitions.

Just create a folder named ".ropeproject" at the root of your project (Rope would do that anyway when a project is initialized).

    cd /path/to/your/project
    mkdir .ropeproject

Then edit any file in this folder or its subfolders and you should get completions, and goto_python_definition should work. Of course, you need to set a key binding, e.g., add this to your user keybindings:

    { "keys": ["super+f3"], "command": "goto_python_definition"}

Getting all completions to work
-------------------------------

Basically, anthing you want completions for has to be on your python path, which you can extend in .ropeprojectconfig.py.

If you are using virtualenv for your project, add the path to the virtualenv in .ropeproject/config.py (there should be a commented-out line already in the file in set_prefs).

    prefs.add('python_path', '/Users/ebi/dev/project/lib/python2.7/site-packages/')

Also, if you are not using the same Python as ST2 (e.g. using a custom Python on OSX), add your site-packages, so that ST2 picks them up

    prefs.add('python_path', '/usr/local/Cellar/python/2.7.1/lib/python2.7/site-packages')

A special case are Django projects, which use global imports and not relative ones, e.g., in views.py they use "import Project.App.models" and not just "import models". In this case, you project has to be on the Python path as well. Add the parent dir of your project:

    prefs.add('python_path', '/Users/ebi/my_django_projects')


Refactoring functions
---------------------

SublimeRope now supports the Rope refactoring function "Rename", which renames an identifier (function, class, variable etc.) throughout your project. To use it, you will need to set a keybinding:

    { "keys": ["alt+super+r"], "command": "python_refactor_rename"}


Donations
------

Here you go:

<form action="https://www.paypal.com/cgi-bin/webscr" method="post">
<input type="hidden" name="cmd" value="_s-xclick">
<input type="hidden" name="hosted_button_id" value="EVBU58TZPQH8J">
<input type="image" src="https://www.paypalobjects.com/WEBSCR-640-20110429-1/en_US/i/btn/btn_donate_SM.gif" border="0" name="submit" alt="PayPal - The safer, easier way to pay online!">
<img alt="" border="0" src="https://www.paypalobjects.com/WEBSCR-640-20110429-1/de_DE/i/scr/pixel.gif" width="1" height="1">
</form>

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