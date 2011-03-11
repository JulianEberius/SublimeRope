import sys, site

def update_python_path(paths):
    "update sys.path and make sure the new items come first"
    old_sys_path_items = list(sys.path)
    
    for path in paths:
        # see if it is a site dir
        if path.find('site-packages') != -1:
            site.addsitedir(path)
        else:
            sys.path.insert(0, path)

    # Reorder sys.path so new directories at the front.
    new_sys_path_items = set(sys.path) - set(old_sys_path_items)
    sys.path = list(new_sys_path_items) + old_sys_path_items
