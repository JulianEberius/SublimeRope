.. _cache_mechanisms:


===============================
Cache Mechanisms in SublimeRope
===============================

Rope library uses binary cache files in order to offer auto completion, import assist, jump to global and documentation features. There exists various ways of generate and/or regenerate those cache files using SublimeRope.

The old way: editing Rope python path
=====================================
.. note::
    This is *NOT* the recommended way of settings cache for get all auto completions working.

Basically, anything you want completions for (or auto import, jump to globals, documentation) has to be in the Rope's python path. You can extend the Rope's python path editing the ``.ropeproject/config.py`` (If you don't know what ``.ropeproject`` directory is you should look at :ref:`create_project`)

If you are using `virtualenv <http://www.virtualenv.org/en/latest/>`_ for your project, add the path to the ``virtualenv`` in ``.ropeproject/config.py`` if you don't set it at project creation (there should be a commented-out already line in the ``set_prefs`` configuration key in the file)::

    prefs.add('python_path', '/Users/<username>/Development/Twisted-12.0/')

Also, if you are not using the same Python as ST2 (e.g. using a custom Python os OSX or using the latest Ubuntu release), add your site-packages (dist-packages in some Linux distributions), so that ST2 picks them up::

    prefs.add('python_path', '/usr/lib/python2.7/site-packages')

A special case are Django projects, which use global imports and not relative ones, e.g., in views.py they use "import Project.App.models" and not just "import models". In this case, you project has to be on the Python path as well. Add the parent dir of your project::

    prefs.add('python_path', '/Users/<username>/my_django_projects')
