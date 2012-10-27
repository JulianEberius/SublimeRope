.. _key_bindings:

============
Key Bindings
============

SublimeRope provides no default keybindings at the moment, so you need to set them yourself. We suggest this bindings as a template that you can modify at your convenience::

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
    { "keys": ["ctrl+r", "ctrl+v"], "command": "python_refactor_extract_variable", "context":
        [
            { "key": "selector", "operator": "equal", "operand": "source.python" }
        ]
    },
    { "keys": ["ctrl+r", "ctrl+n"], "command": "python_refactor_inline_variable", "context":
        [
            { "key": "selector", "operator": "equal", "operand": "source.python" }
        ]
    },
    { "keys": ["ctrl+r", "ctrl+j"], "command": "python_jump_to_global", "context":
        [
            { "key": "selector", "operator": "equal", "operand": "source.python" }
        ]
    },
    { "keys": ["ctrl+r", "ctrl+i"], "command": "python_auto_import", "context":
        [
            { "key": "selector", "operator": "equal", "operand": "source.python" }
        ]
    },
    { "keys": ["ctrl+r", "ctrl+c"], "command": "python_regenerate_cache", "context":
        [
            { "key": "selector", "operator": "equal", "operand": "source.python" }
        ]
    },
    { "keys": ["ctrl+r", "ctrl+f"], "command": "python_refactor_restructure", "context":
        [
            { "key": "selector", "operator": "equal", "operand": "source.python"}
        ]
    },
    { "keys": ["ctrl+r", "ctrl+m"], "command": "python_generate_modules_cache", "context":
        [
            { "key": "selector", "operator": "equal", "operand": "source.python"}
        ]
    },
    { "keys": ["ctrl+alt+space"], "command": "python_manual_completion_request", "context":
        [
            { "key": "selector", "operator": "equal", "operand": "source.python" }
        ]
    },
