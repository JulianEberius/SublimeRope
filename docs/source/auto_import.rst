.. _auto_import:

===========
Auto Import
===========

SublimeRope offers auto importing features through Rope library. It looks for possible imports from the project starting with the prefix under the cursor.

In order to use auto import you should look for ``Rope: Import Assist`` in the Control Palette or just add a shortcut in your configuration. We provide a serie of possible :ref:`key_bindings` in this Documentation as well.

Auto Import Improvements
========================

When Auto Import Improvements are enabled all the undefined

You can enable Auto Import Improvements in your SublimeRope's settings file just setting the ``use_autoimport_improvements`` to true if you feels that its not slowing down your ST2.

Future Plans
============

Improving the Auto Import feature is being considered by some SublimeRope contributors.

Some Considerations
===================

The list of modules that you will get when doing auto import is determined by the :ref:`cache_mechanisms`.
