.. _cache_mechanisms:


===============================
Cache Mechanisms in SublimeRope
===============================

Rope library uses binary cache files to offer auto completion, import assist, jump to global and documentation features. Exists different ways of generate and/or regenerate those cache files using SublimeRope.

The Project Cache
=================

When you create a new Rope project, you should use the SublimeRope command Regenerate Project Cache to get the autocompletion, jumps, documentation and auto imports working for the modules under your project root.

This action can be archieved using the ST2 Command Palette.

The old way: editing Rope python path
=====================================
.. warning::
    This is *NOT* the recommended way of settings cache to get all auto completions working anymore.

Basically, anything you want completions for (or auto import, jump to globals, documentation) has to be in the Rope's python path. You can extend the Rope's python path editing the ``.ropeproject/config.py`` (If you don't know what ``.ropeproject`` directory is you should look at :ref:`create_project`)

If you are using `virtualenv <http://www.virtualenv.org/en/latest/>`_ for your project, add the path to the ``virtualenv`` in ``.ropeproject/config.py`` if you don't set it at project creation (there should be a commented-out already line in the ``set_prefs`` configuration key in the file)::

    prefs.add('python_path', '/Users/<username>/Development/Twisted-12.0/')

Also, if you are not using the same Python as ST2 (e.g. using a custom Python os OSX or using the latest Ubuntu release), add your site-packages (dist-packages in some Linux distributions), so that ST2 picks them up::

    prefs.add('python_path', '/usr/lib/python2.7/site-packages')

A special case are Django projects, which use global imports and not relative ones, e.g., in views.py they use "import Project.App.models" and not just "import models". In this case, you project has to be on the Python path as well. Add the parent dir of your project::

    prefs.add('python_path', '/Users/<username>/my_django_projects')

The new way: adding modules to Autoimport Modules List
======================================================


This is the recommended way of get global modules auto imports and friends working.

You can also get autocompletion and friends working for modules not under your project root simply adding them to the list of ``autoimport_modules`` in your ``SublimeRope.sublime-settings`` file and then run the ``Regenerate Global Module Cache`` command from ST2 Command Palette or generating a key binding for it.

.. note::

    Take care, there is also another command, ``Regenerate Project Cache``, which rebuilds the cache just for your project not for global modules.

You can specify ``rope_autoimport_modules`` in your project settings instead of your global ``SublimeRope.sublime-settings`` file.

.. note::
    note that although using the global configuration file works, using your project settings file is the recommended way

To archieve this you should navigate to ``Project->Edit Project`` and add your modules there in the ``settings`` section. If this section doesn't exists just create it::

    "settings":
    {
        "rope_autoimport_modules":
        [
            "twisted.*",
            "numpy.*",
            "libsaas.*",
            ...
        ]
    }

.. warning::

    Non-trivial/nested modules like numpy or twisted will have to be added in the form ``twisted.*`` or Rope will not index them correctly.
