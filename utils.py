import sublime

def get_setting(key, default_value=None):
    try:
        settings = sublime.active_window().active_view().settings()
        if settings.has('rope_{0}'.format(key)):
            return settings.get('rope_{0}'.format(key))
    except:
        pass
    s = sublime.load_settings('SublimeRope.sublime-settings')
    return s.get(key, default_value)