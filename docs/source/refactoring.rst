.. _refactoring:

===========
Refactoring
===========

SublimeRope offers a few refactors through Rope library.

Renaming
========

Consider the following code::

    class First(object):
        """First Class"""
        def __init__(self):
            self.id = 1

        def change_id(self, arg):
            self.id = id

        def print_id(self):
            print self.id

    first = First()
    first.change_id(123)
    first.print_id()

We can just put the cursor over id in the ``__init__`` method and rename it to ``new_id`` after that our code should looks like::

    class First(object):
        """First Class"""
        def __init__(self):
            self.new_id = 1

        def change_id(self, arg):
            self.new_id = new_id

        def print_id(self):
            print self.new_id

    first = First()
    first.change_id(123)
    first.print_id()

After renaming ``print_id`` method to ``identify_me`` all the references in our project should change to our new function name.

.. note::

    ST2 already offer some interesting features to archieve the same results really fast

Extract Method
==============

Let's imagine we have the following code::

    def some_func():
        a = 10
        b = 20
        c = ``a * 2 + b * 3``

After performing extract method of the highlighted operation above we should get::

    def some_func():
        a = 10
        b = 20
        c = new_func(a, b)

    def new_func(a, b):
        return a * 2 + b * 3

Extracting Decorated Methods
============================

Extract method can handle static and class methods that use the decorators ``@staticmethod`` and ``@classmethod`` as for example in::

    class First(object):

        @staticmethod
        def a_method(arg):
            aux = arg * 2

After extract a * 2 as a method called ``twice`` we should get::

    class First(object):

        @staticmethod
        def a_method(arg):
            aux = First.twice(arg)

        @staticmethod
        def twice(arg):
            return arg * 2

Extract Variable
================

Imagine we have this expression::

    x = 2 * 3

After extract a variable with name ``six`` we should have::

    six = 2 * 3
    x = six

Restructuring
=============

A restructuring is a program transformation; not as well defined as other refactorings like rename. In its basic form, we have a ``pattern`` and a ``goal``. Consider we were not aware of the ``**`` operator and wrote our own::

    def pow(x, y):
        result = 1
        for i in range(y);
            result *= x
        return result

    print pow(2, 3)

When we realice that ``**`` exists we want to use it wherever ``pow`` is used. We can use a pattern like::

    pattern: pow(${param1} ** ${param2})

Goal can be something like::

    goal: ${param1} ** ${param2}

The matched names in pattern should be replaced with the string that was matched in each occurrence. So the outcome of the restructuring should be::

    def pow(x, y):
        result = 1
        for i in range(y):
            result *= x
        return result

    print 2 ** 3

It seems to be working but what if pow is imported in some module or we have some other function defined in some other module that uses the same name and we don't want to change it. Wildcard arguments come to rescue. Wildcard arguments is a mapping; Its keys are wildcard names that appear in the pattern (the names inside ``${...}``).

The values are the parameters that are passed to wildcard matchers. The arguments a wildcard takes is based on its type.

For checking the type of a wildcard, we can pass ``type=value`` as an argument; value should be resolved to a python variable (or reference). For instance for specifying ``pow`` in this example we can use ``mod.pow``. As you see, this string should start from module name. For referencing python builtin types and functions you can use ``__builtin__`` module (for instance ``__builtin__.int``).

For solving the mentioned problem, we change our pattern. But goal remains the same::

    pattern: ${pow_func} (${param1}, ${param2})
    goal: ${param1} ** ${param2}

Consider the name of the module containing our ``pow`` function is ``mod``.  args can be::

    pow_func: name=mod.pow

If we need to pass more arguments to a wildcard matcher we can use , to separate them. Such as name: ``type=mod.MyClass,exact``.

This restructuring handles aliases; like in::

    mypow = pow
    result = mypow(2, 3)
    Transforms into:

    mypow = pow
    result = 2 ** 3

If we want to ignore aliases we can pass exact as another wildcard argument::

    pattern: ${pow}(${param1}, ${param2})
    goal: ${param1} ** ${param2}
    args: pow: name=mod.pow, exact

``${name}``, by default, matches every expression at that point; if exact argument is passed to a wildcard only the specified name will match (for instance, if exact is specified , ``${name}`` matches name and x.name but not var nor (1 + 2) while a normal ``${name}`` can match all of them).
