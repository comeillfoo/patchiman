#!/usr/bin/env python3
import os
from typing import Tuple
import errno
import shutil
import click
import tempfile

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
VERBOSE = False


def _echo(text: str):
    if VERBOSE: click.echo(text)


def _print_result(patch: str, rc: PatchResult = PatchResult.ERROR):
    if rc == PatchResult.OK:
        click.echo(f'{OK} {patch}')
    elif rc == PatchResult.HUNK_SUCCEED:
        click.echo(f'{WARN} {patch} (Consider running dehunk command)')
    else:
        click.echo(f'{NOTOK} {patch} ({PATCH_ERROR_REASONS[rc]})')


def _redeploy(src: str, dst: str):
    shutil.rmtree(dst)
    shutil.copytree(src, dst)


def init_dirs(tmpdir, source) -> Tuple[str, str]:
    def _make_pathes(dir: str) -> Tuple[str, str]:
        return ('a', 'b') if dir == '.' else (os.path.join(dir, 'a'), os.path.join(dir, 'b'))

    def _isdirs_or_die(*directories):
        for directory in directories:
            if not os.path.isdir(directory):
                click.echo(f'{directory} not found')
                exit(errno.ENOENT)
            _echo(f'{directory} exists')

    dira, dirb = _make_pathes(tmpdir)
    shutil.copytree(source, dira)
    shutil.copytree(dira, dirb)
    _isdirs_or_die(dira, dirb)
    return dira, dirb


def at_tempdir(callback) -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        return callback(tmpdir)


@click.group()
@click.option('-v', '--verbose', count=True, help='Output extra information.')
def cli(verbose: bool):
    global VERBOSE
    VERBOSE = verbose


@cli.command()
@click.option('-C', '--directory', default=os.getcwd(),
              type=click.Path(exists=True, file_okay=False, dir_okay=True),
              help='Path where compared directories (a, b)')
@click.argument('patches', nargs=-1,
                type=click.Path(exists=True))
def apply(directory: str, patches):
    """Tries to apply patches."""
    def do_apply(tmpdir) -> int:
        fails = 0
        dira, dirb = init_dirs(tmpdir, directory)

        for patch in patches:
            rc = _patch(_echo, dirb, patch, ['-d'])
            _print_result(patch, rc)
            if not rc.is_ok():
                fails += 1
                _redeploy(dira, dirb)
        return fails

    exit(at_tempdir(do_apply))


@cli.command()
@click.option('-C', '--directory', default=os.getcwd(),
              type=click.Path(exists=True, file_okay=False, dir_okay=True),
              help='Path where compared directories (a, b)')
@click.argument('patches', nargs=-1,
                type=click.Path(exists=True))
def dehunk(directory: str, patches):
    """Excludes succesful hunks in patches."""
    def do_dehunk(tmpdir) -> int:
        fails = 0
        dira, dirb = init_dirs(tmpdir, directory)
        applied = []

        for patch in patches:
            rc = _patch(_echo, dirb, patch, ['-d'])
            _print_result(patch, rc)
            if rc == PatchResult.HUNK_SUCCEED:
                # with hunks to .orig
                shutil.copyfile(patch, patch + '.orig')
                dehunked = _diff(_echo, dira, dirb, ['-x', '*.orig'])
                if dehunked is None:
                    click.echo(f'Failed to dehunk {patch}')
                    exit(fails)
                with open(patch, 'w') as p:
                    p.write(dehunked)
                applied.append(patch)
            elif rc == PatchResult.OK:
                applied.append(patch)
                _echo(f'no hunks for {patch} -- SKIP')
            else:
                fails += 1
                applied = []
        _redeploy(dira, dirb)
        return fails

    exit(at_tempdir(do_dehunk))


@cli.command()
@click.option('-C', '--directory', default=os.getcwd(),
              type=click.Path(exists=True, file_okay=False, dir_okay=True),
              help='Patched directory')
@click.argument('patches', nargs=-1,
                type=click.Path(exists=True))
def revert(directory: str, patches):
    """Reverts patches."""
    for patch in reversed(patches):
        _echo(f'reverting {patch}...')
        rc = _revert(directory, patch, ['-d'])
        _print_result(patch, rc)
        if not rc.is_ok():
            exit(1)


if __name__ == '__main__':
    cli()