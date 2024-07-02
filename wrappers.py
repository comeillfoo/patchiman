import enum
import re
from typing import Optional
import subprocess as sp
import logclick as logging



class PatchResult(enum.Enum):
    OK = 0
    REVERSE_APPLIED = 1
    HUNK_SUCCEED = 2
    HUNK_FAILED = 3
    INVALID_FORMAT = 4
    FILE_NOT_FOUND = 5
    EOF = 6
    ERROR = 7

    def is_ok(self) -> bool:
        return self == PatchResult.OK or self == PatchResult.HUNK_SUCCEED


PATCH_ERROR_REASONS = {
    PatchResult.REVERSE_APPLIED: 'Already applied',
    PatchResult.HUNK_FAILED: 'Hunk failed',
    PatchResult.INVALID_FORMAT: 'Invalid format',
    PatchResult.FILE_NOT_FOUND: 'Can\'t find file to patch',
    PatchResult.EOF: 'Unexpected end of patch',
    PatchResult.ERROR: 'Error',
}


def _diff(a: str, b: str, extra_args: list[str]) -> Optional[str]:
    cmd = ['diff', '-updrN', *extra_args, a, b]
    logging.subcommand(' '.join([cmd[0].upper()] + cmd[1:]))
    p = sp.Popen(cmd,
                 stdout=sp.PIPE, stderr=sp.PIPE, text=True)
    stdout, stderr = p.communicate()
    logging.subcommand(f'stdout: {stdout.strip()}')
    logging.subcommand(f'stderr: {stderr.strip()}')
    return stdout if p.returncode != 2 else None


def _patch(target: str, patch: str, extra_args: list[str]) -> PatchResult:
    cmd = ['patch', '-p1', '-F0', *extra_args, target]
    logging.subcommand(' '.join([cmd[0].upper()] + cmd[1:]))
    p = sp.Popen(cmd,
                 stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = '', ''
    with open(patch, 'rb') as f:
        stdout, stderr = p.communicate(input=f.read())
        stdout, stderr = stdout.decode(), stderr.decode()
    logging.subcommand(f'stdout: {stdout.strip()}')
    logging.subcommand(f'stderr: {stderr.strip()}')
    if p.returncode == 0:
        if re.search('Hunk\s*#\d+\s*succeeded', stdout) is not None:
            return PatchResult.HUNK_SUCCEED
        return PatchResult.OK

    if 'patch: ****' in stderr:
        is_gibberish = 'Only garbage was found in the patch input.' in stderr
        is_malformed = 'malformed patch at' in stderr
        if is_gibberish or is_malformed:
            return PatchResult.INVALID_FORMAT
        elif 'unexpected end of file in patch' in stderr:
            return PatchResult.EOF
        return PatchResult.ERROR

    is_partly_succeeded = re.search('(patching\s*.*\n(Hunk\s*#\d+\s*succeeded.*\n)?){2,}', stdout) is not None
    is_hunk_failed = re.search('Hunk\s*#\d+\s*FAILED', stdout) is not None
    if 'Assume -R' in stdout:
        return PatchResult.HUNK_FAILED if is_partly_succeeded else PatchResult.REVERSE_APPLIED
    elif 'can\'t find file to patch' in stdout:
        return PatchResult.HUNK_FAILED if is_partly_succeeded else PatchResult.FILE_NOT_FOUND
    return PatchResult.HUNK_FAILED if is_hunk_failed or is_partly_succeeded else PatchResult.ERROR

def _revert(target: str, patch: str, extra_args: list[str]) -> PatchResult:
    return _patch(target, patch, ['-R', *extra_args])
