.. _auto_completion:

===============
Auto Completion
===============

ST2 offers three types of completions itself:

* Word completions (complete from words present on the current buffer)
* Explicit completions (those that you can define in syntax-specific files, such as ``Python.sublime.completions``)
* Autocompletions from plugins.

.. note::

    Some people prefer to disable the default word and/or explicit completions that ST2 offers while using SublimeRope. This can be archieved by setting either of the following settings to ``true`` in the User Settings for SublimeRope settings in your ST2 Preferences Menú.

    * ``suppress_word_completions``
    * ``suppress_explicit_completions``

Simple Completion
=================

SublimeRope provides completion suggestions based on the rope library, but also offers a fall-back method if rope suggest nothing. Albeit it is sometimes useful, it is disabled by default because some users feels that it slows down the plugin too much.

You can enbale it setting ``use_simple_completion`` to true in SublimeRope settings file.

Howto get autocompletion on dot typing?
===========================================

Some users want SublimeRope shown the completions just after typing the dot in for example  ``os.``, ST2 gives us a simple way to setup this desirable behavior.

We should just edit the ``Python.sublime-settings`` file in ``Package/User`` (or create it in case that you don't have one already). In this way, this behavior should be only applicable to our Python files and not in all the files we edit with ST2::

    "auto_complete_triggers": [ {"selector": "source.python - string - comment - constant.numeroc", "characters": "."} ]

This line makes autocomplete not appear when we type dot inside strings or comments but fails with literal hexadecimal number (seems to be a bug in ST2 itself).

Some Considerations
===================

The list of completions that you will get back when auto completion triggers is determined by the :ref:`cache_mechanisms`.
