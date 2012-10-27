.. _auto_completion:

===============
Auto Completion
===============

ST2 offers three types of completions itself:

* Word completions (complete from words present on the current buffer)
* Explicit completions (those that you can define in syntax-specific files, such as ``Python.sublime.completions``)
* Autocompletions from plugins.

.. note::

    Some people prefer to disable the default word and/or explicit completions that ST2 offers while using SublimeRope. This can be achieved by setting either of the following settings to ``true`` in the User Settings for SublimeRope settings in your ST2 Preferences Menú.

    * ``suppress_word_completions``
    * ``suppress_explicit_completions``

Manual Completions
==================

On larger projects, generating the completion proposals can take a noticeable amount of time. Waiting half a second is no problem usually, but with ST2 automatic as-you-type completions it can slow down your typing.
Just set the "complete_as_you_type" option in your SublimeRope.sublime_settings or in your project settings as "rope_complete_as_you_type" to false, and you will only get the lightning fast buffer-based completions from ST2. Then you can manually trigger the more intelligent Rope-based completions using the "PythonManualCompletionRequestCommand".
Bind it to some nice key, e.g. ctrl+alt+space, and you can get them easily when you need them.

Simple Completion
=================

SublimeRope provides completion suggestions based on the rope library, but also offers a fall-back method if rope suggest nothing. Albeit it is sometimes useful, it is disabled by default because some users feels that it slows down the plugin too much.

You can enable it setting ``use_simple_completion`` to true in SublimeRope settings file.

Howto get autocompletion on dot typing?
===========================================

Some users want SublimeRope shown the completions just after typing the dot in for example  ``os.``, ST2 gives us a simple way to setup this desirable behavior.

We should just edit the ``Python.sublime-settings`` file in ``Package/User`` (or create it in case that you don't have one already). In this way, this behavior should be only applicable to our Python files and not in all the files we edit with ST2::

    "auto_complete_triggers": [ {"selector": "source.python - string - comment - constant.numeroc", "characters": "."} ]

This line makes autocomplete not appear when we type dot inside strings or comments but fails with literal hexadecimal number (seems to be a bug in ST2 itself).

Some Considerations
===================

The list of completions that you will get back when auto completion triggers is determined by the :ref:`cache_mechanisms`.
