#!/usr/bin/python3
import shutil
import os
from typing import Tuple

import logclick as logging


STORAGE_ROOT = '.patchiman'
PATCHES_CATEGORIES = [ 'committed', 'postponed', 'original' ]

_is_patch = lambda path: str.endswith(path, '.patch')
_storage_path = lambda root: os.path.join(root, STORAGE_ROOT)


def test(project_root: str) -> Tuple[bool, str]:
    storage_path = _storage_path(project_root)
    if not os.path.isdir(storage_path):
        return False, 'storage not exists'
    for patches_category in PATCHES_CATEGORIES:
        category_path = os.path.join(storage_path, patches_category)
        if not os.path.isdir(category_path):
            return False, 'broken storage, ' + patches_category + ' not found'
    return True, ''


def relink(project_root: str) -> Tuple[bool, str]:
    def _find_patches(folder: str) -> map:
        return map(lambda patch: os.path.join(folder, patch),
                   filter(_is_patch, os.listdir(folder)))

    for patch in _find_patches(project_root):
        try:
            os.remove(patch)
            logging.subcommand(patch + ' removed')
        except Exception as e:
            return False, 'failed to delete \'' + patch + '\': ' + str(e)

    committed_path = os.path.join(_storage_path(project_root), 'committed')
    for patch in _find_patches(committed_path):
        try:
            source = os.path.relpath(patch, project_root)
            target = os.path.join(project_root, os.path.basename(patch))
            os.symlink(source, target)
            logging.subcommand('symlinked ' + source + ' -> ' + target)
        except Exception as e:
            return False, 'failed to symlink \'' + patch + '\': ' + str(e)
    return True, ''


def init(project_root: str) -> Tuple[bool, str]:
    storage_path = _storage_path(project_root)
    shutil.rmtree(storage_path, ignore_errors=True)
    for patches_category in PATCHES_CATEGORIES:
        category_path = os.path.join(storage_path, patches_category)
        os.makedirs(category_path)
        logging.subcommand(f'{patches_category} initialized')
    return True, ''


def postpone(project_root: str, patch: str) -> Tuple[bool, str]:
    storage_path = _storage_path(project_root)
    original_path = os.path.join(storage_path, 'original', patch)
    postponed_path = os.path.join(storage_path, 'postponed', patch)
    if not os.path.isfile(original_path):
        return False, 'not exists'
    try:
        shutil.move(original_path, postponed_path)
    except Exception as e:
        return False, str(e)

    return True, ''

