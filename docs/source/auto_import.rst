.. _auto_import:

===========
Auto Import
===========

SublimeRope offers auto importing features through Rope library. It looks for possible imports from the project starting with the prefix under the cursor.

In order to use auto import you should look for ``Rope: Import Assist`` in the Control Palette or just add a shortcut in your configuration. We provide a serie of possible :ref:`key_bindings` in this Documentation as well.

Auto Import Improvements
========================

When Auto Import Improvements are enabled all the undefined words in the current file should be checked (in a different thread) looking for an auto import for them. If SublimeRope finds a possible autoimport for them should show you so you can choose it and the import will be automatically applied to your file.

You can disable Auto Import Improvements in your SublimeRope's settings file just setting the ``use_autoimport_improvements`` to false if you feels that its slowing down your ST2.


Some Considerations
===================

The list of modules that you will get when doing auto import is determined by the :ref:`cache_mechanisms`.
