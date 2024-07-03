#!/usr/bin/python3
import shutil
import os
from typing import Tuple

import logclick as logging


STORAGE_ROOT = '.patchiman'

_is_patch = lambda path: str.endswith(path, '.patch')


def relink(project_root: str) -> Tuple[bool, str]:
    return False, 'not implemented yet'
    storage_path = os.path.join(project_root, STORAGE_ROOT)
    if not os.path.isdir(storage_path):
        return False, project_root + ' doesn\'t have an initialized storage'

    for patch_path in filter(_is_patch, os.listdir(storage_path)):
        try:
            os.remove(patch_path)
        except Exception as e:
            return False, 'failed to delete \'' + patch_path + '\': ' + str(e)

    # TODO: create symlinks to files in committed directory
    return True, ''


def init(project_root: str) -> Tuple[bool, str]:
    storage_path = os.path.join(project_root, STORAGE_ROOT)
    shutil.rmtree(storage_path, ignore_errors=True)
    for patches_category in [ 'committed', 'postponed', 'original' ]:
        category_path = os.path.join(storage_path, patches_category)
        os.makedirs(category_path)
        logging.subcommand(f'{patches_category} initialized')
    return True, ''
