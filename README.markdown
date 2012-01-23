**SublimeRope**
===========================

Adds Python completions and some IDE-like functions to Sublime Text 2, through the use of the [Rope](http://rope.sourceforge.net/) library.

I have tested it on the latest dev build. It seems to work equally well on OSX, Linux and Windows, though I mostly test on OSX.
No guarantees here!

Copyright (C) 2011 Julian Eberius

Basic Usage
-----------

Just unzip / git clone the folder SublimeRope into ST2's Packages folder. Basic completion should work (for more, see below) and all the commands should be reachable through the Command Palette.

**IMPORTANT**: Since ST2 for the moment has no API to find or mark the project root folder, if you want completions from your whole project and not just one file, you have to mark your project's root, so that Rope knows which folders to scan for completions / definitions.

To do so, call the command "Rope: New Project" from the command palette. This will ask you for the
project root directory and for the root of the virtualenv. Leave the second one empty if you don't use virtualenv.

Available Commands:

* Go to Definition
* Show Documentation
* Jump to Global
* Refactor: Rename
* Refactor: Extract Method
* And, of course, completions, which hook into Sublime's normal completion system (Ctrl+Space)

Key Bindings
------------

SublimeRope provides no default keybindings, so you need to set them yourself. The bindings I use:

    { "keys": ["ctrl+r", "ctrl+d"], "command": "goto_python_definition", "context":
        [
            { "key": "selector", "operator": "equal", "operand": "source.python" }
        ]
    },
    { "keys": ["ctrl+r", "ctrl+h"], "command": "python_get_documentation", "context":
        [
            { "key": "selector", "operator": "equal", "operand": "source.python" }
        ]
    },
    { "keys": ["ctrl+r", "ctrl+r"], "command": "python_refactor_rename", "context":
        [
            { "key": "selector", "operator": "equal", "operand": "source.python" }
        ]
    },
    { "keys": ["ctrl+r", "ctrl+e"], "command": "python_refactor_extract_method", "context":
        [
            { "key": "selector", "operator": "equal", "operand": "source.python" }
        ]
    },
    { "keys": ["ctrl+r", "ctrl+c"], "command": "python_regenerate_cache", "context":
        [
            { "key": "selector", "operator": "equal", "operand": "source.python" }
        ]
    },
    { "keys": ["ctrl+r", "ctrl+j"], "command": "python_jump_to_global", "context":
        [
            { "key": "selector", "operator": "equal", "operand": "source.python" }
        ]
    },


Getting all completions to work
-------------------------------

Basically, anthing you want completions for has to be on Rope's python path, which you can extend in <PROJECT_DIR>/.ropeproject/config.py.

If you are using virtualenv for your project, add the path to the virtualenv in .ropeproject/config.py (there should be a commented-out line already in the file in set_prefs). *UPDATE*: the "Rope: New Project" command should do this for you.

    prefs.add('python_path', '/Users/ebi/dev/project/lib/python2.7/site-packages/')

Also, if you are not using the same Python as ST2 (e.g. using a custom Python on OSX), add your site-packages, so that ST2 picks them up

    prefs.add('python_path', '/usr/local/Cellar/python/2.7.1/lib/python2.7/site-packages')

A special case are Django projects, which use global imports and not relative ones, e.g., in views.py they use "import Project.App.models" and not just "import models". In this case, you project has to be on the Python path as well. Add the parent dir of your project:

    prefs.add('python_path', '/Users/ebi/my_django_projects')


Donations
---------

Here you go:

[![PayPal - The safer, easier way to pay online!](https://www.paypalobjects.com/WEBSCR-640-20110429-1/en_US/i/btn/btn_donate_SM.gif)](https://www.paypal.com/us/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=EVBU58TZPQH8J)

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
