.. _getting_started:


***************
Getting started
***************

Ready to get started? This page gives you a basic introduction to SublimeRope. If you're looking for detailed information about auto completions go to :ref:`auto_completion` page. For information about refectoring go to :ref:`refactoring` page.

.. _whats-sublimerope:

SublimeRope
===========

SublimeRope adds Python completions and some IDE-like functions to Sublime Text 2, through the use of the `Rope <http://rope.sourceforge.net/>`_ library.

SublimeRope has been tested on the latest dev build working well on OSX, Linux and Windows.

Basic Usage
___________

Just unzip / git clone the folder SublimeRope into ST2's Packages folder. Basic completion should work and all commands should be reachable through the Command Palette.

Using Package Control
_____________________

The recommended way to install SublimeRope into ST2 is by using `Package Control <http://wbond.net/sublime_packages/package_control>`_.

Available Commands
__________________

* Completions, which hook into Sublime's normal completion system (Ctrl+Space and as-you-type)
* Go to Definition
* Show Documentation
* Refactor->Rename
* Refactor->Extract Method
* Refactor->Extract Variable
* Refactor->Inline Variable
* Refactor->Restructure
* Jump to Global: Shows a list of project globals in a quickview and allows to jump to them.
* Import assist: Looks for possible imports from the project starting with the prefix under the cursor. Will automatically insert the "from X import Z" statement.
* Regenerate Global Module Cache
* Regenerate Project Cache

Some notes
==========

SublimeRope is a Free Software project developed and maintained by Julian Eberius and a few collaborators in their free time. To review a full list of SublimeRope developers just look at the project's `GitHub Page <https://github.com/JulianEberius/SublimeRope>`_.

License
_______

Sublime Rope is distributed under the Free Software Foundation General Public License terms::

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

Have a look at `LICENSE.txt <https://github.com/JulianEberius/SublimeRope/blob/master/LICENSE.txt>`_ file for more information.

.. note::

    This project uses code from other open source projects (Rope) which may include licenses of their own.
