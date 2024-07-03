# patman

Patch manager. Helps in testing patches applicability. Manages patches using folder
as storage. A storage arranges patches into next categories:

- `committed` - ready to send, publish, use and etc
- `original` - first versions of patches
- `postponed` - set of deferred patches because of inapplicability

## Usage:

`patchiman [OPTIONS] COMMAND [ARGS]...`

## Options:

- `-v, --verbose`
  + Output extra information.
- `--help`
  + Show this message and exit.

## Commands:

- `apply`
  + Tries to apply patches.
- `dehunk`
  + Excludes succesful hunks in patches.
- `revert`
  + Reverts patches.