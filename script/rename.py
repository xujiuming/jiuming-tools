#!/bin/bash/python3

# author ming
# rename filename
import os

root_path = '/mnt/c/Users/ming/Desktop/workspaces/jiuming-tools/script'
rename_symbol_map = {
    "_": "-",
    "1": "2",
}


def rename_symbol(root, name, s, rename_symbol_map):
    old_path = os.path.join(root, name)
    name = name.replace(s, rename_symbol_map.get(s))
    new_path = os.path.join(root, name)
    print("{}重命名为:{}".format(old_path, new_path))
    os.rename(old_path, new_path)
    return name


for root, dirs, files in os.walk(root_path, topdown=False):
    for name in files:
        for s in rename_symbol_map.keys():
            if s in name:
                name = rename_symbol(root, name, s, rename_symbol_map)
    for name in dirs:
        for s in rename_symbol_map.keys():
            if s in name:
                name = rename_symbol(root, name, s, rename_symbol_map)
