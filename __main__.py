#!/usr/bin/env python3
import os
from typing import Tuple
import errno
import shutil
import click
import tempfile
import logclick as logging
import storage

from wrappers import _patch, _revert, _diff, PatchResult, PATCH_ERROR_REASONS


class TextStyle:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


OK = f'{TextStyle.BOLD}{TextStyle.GREEN}\u2713{TextStyle.END}'
NOTOK = f'{TextStyle.BOLD}{TextStyle.RED}\u2717{TextStyle.END}'
WARN = f'{TextStyle.BOLD}{TextStyle.YELLOW}\u26a0{TextStyle.END}'
VERBOSE = 0


def _print_result(patch: str, rc: PatchResult = PatchResult.ERROR):
    if rc == PatchResult.OK:
        click.echo(f'{OK} {patch}')
    elif rc == PatchResult.HUNK_SUCCEED:
        click.echo(f'{WARN} {patch} (Consider running dehunk command)')
    else:
        click.echo(f'{NOTOK} {patch} ({PATCH_ERROR_REASONS[rc]})')


def _redeploy(src: str, dst: str):
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src, dst)


def init_dirs(tmpdir, source) -> Tuple[str, str]:
    def _make_pathes(dir: str) -> Tuple[str, str]:
        return ('a', 'b') if dir == '.' else (os.path.join(dir, 'a'), os.path.join(dir, 'b'))

    def _isdirs_or_die(*directories):
        for directory in directories:
            if not os.path.isdir(directory):
                logging.error(f'{directory} not found')
                exit(errno.ENOENT)
            logging.info(f'{directory} exists')

    dira, dirb = _make_pathes(tmpdir)
    _redeploy(source, dira)
    _redeploy(dira, dirb)
    _isdirs_or_die(dira, dirb)
    return dira, dirb


def at_tempdir(callback) -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        return callback(tmpdir)


@click.group()
@click.option('-v', '--verbose', count=True, help='Output extra information.')
def cli(verbose: int):
    verbose += logging.get_loglevel().value
    new_log_level = logging.LogClickLevel.from_int(verbose)
    logging.set_loglevel(new_log_level)


@cli.command()
@click.option('-C', '--directory', default=os.getcwd(),
              type=click.Path(exists=True, file_okay=False),
              help='Path to project directory')
@click.argument('patches', nargs=-1,
                type=click.Path(exists=True, dir_okay=False))
def apply(directory: str, patches):
    """Tries to apply patches."""
    def do_apply(tmpdir) -> int:
        fails = 0
        dira, dirb = init_dirs(tmpdir, directory)

        for patch in patches:
            rc = _patch(dirb, patch, ['-d'])
            _print_result(patch, rc)
            if not rc.is_ok():
                fails += 1
                _redeploy(dira, dirb)
        return fails

    exit(at_tempdir(do_apply))


@cli.command()
@click.option('-C', '--directory', default=os.getcwd(),
              type=click.Path(exists=True, file_okay=False),
              help='Path to project directory')
@click.argument('patches', nargs=-1,
                type=click.Path(exists=True, dir_okay=False))
def dehunk(directory: str, patches):
    """Excludes succesful hunks in patches."""
    def do_dehunk(tmpdir) -> int:
        fails = 0
        dira, dirb = init_dirs(tmpdir, directory)
        applied = []

        for patch in patches:
            rc = _patch(dirb, patch, ['-d'])
            _print_result(patch, rc)
            if rc == PatchResult.HUNK_SUCCEED:
                shutil.copyfile(patch, patch + '.orig') # with hunks to .orig
                # apply previous applied patch
                for applied_patch in applied:
                    _patch(dira, applied_patch, ['-d'])

                # create dehunked patch
                old_pwd = os.getcwd()
                os.chdir(tmpdir)
                dehunked = _diff('a', 'b', ['-x', '*.orig'])
                os.chdir(old_pwd)

                if dehunked is None:
                    logging.fatal(f'Failed to dehunk {patch}')
                    exit(fails)
                with open(patch, 'w') as p:
                    p.write(dehunked)

                _redeploy(directory, dira)
                applied.append(patch)
            elif rc == PatchResult.OK:
                logging.warn(f'no hunks for {patch} -- SKIP')
                applied.append(patch)
            else:
                fails += 1
                applied = []
                _redeploy(dira, dirb)
        return fails

    exit(at_tempdir(do_dehunk))


@cli.command()
@click.option('-C', '--directory', default=os.getcwd(),
              type=click.Path(exists=True, file_okay=False, writable=True),
              help='Patched directory')
@click.argument('patches', nargs=-1, type=click.Path(exists=True, dir_okay=False))
def revert(directory: str, patches: list[str]):
    """Reverts patches."""
    for patch in reversed(patches):
        logging.command(f'reverting {patch}...')
        rc = _revert(directory, patch, ['-d'])
        _print_result(patch, rc)
        if not rc.is_ok():
            exit(1)


@cli.command()
@click.option('-C', '--project', default=os.getcwd(), help='Project directory',
                type=click.Path(exists=True, file_okay=False, writable=True))
def init(project: str):
    '''Initializes patches storage'''
    is_ok, error_msg = storage.init(project)
    if not is_ok:
        logging.error('patches storage not initialized: ' + error_msg)
        exit(1)
    logging.command('patches storage initialized')


def check_storage(project_root: str):
    is_ok, err_msg = storage.test(project_root)
    if not is_ok:
        logging.error('unable to proceed: ' + err_msg)
        exit(1)


@cli.command()
@click.option('-C', '--project', default=os.getcwd(), help='Project directory',
                type=click.Path(exists=True, file_okay=False, writable=True))
@click.argument('patches', nargs=-1, type=click.Path())
def postpone(project: str, patches: list[str]):
    '''Postpones patches'''
    check_storage(project)

    for patch in patches:
        is_ok, err_msg = storage.postpone(project, patch)
        if not is_ok:
            logging.warn('unable to postpone ' + patch + ' (SKIP): ' + err_msg)
        logging.command(patch + ' postponed')


@cli.command()
@click.option('-C', '--project', default=os.getcwd(), help='Project directory',
                type=click.Path(exists=True, file_okay=False, writable=True))
def relink(project: str):
    '''Symlinks committed patches to project directory'''
    check_storage(project)
    is_ok, err_msg = storage.relink(project)
    if not is_ok:
        logging.error('unable to relink: ' + err_msg)
    logging.command('relink finished')

if __name__ == '__main__':
    cli()