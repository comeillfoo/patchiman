#!/urs/bin/python3
from enum import IntEnum, auto
import click


class LogClickLevel(IntEnum):
    FATAL = 0
    ERROR = auto()
    WARNING = auto()
    INFO = auto()
    CMD = auto()
    SUBCMD = auto()
    DEBUG = auto()

    @classmethod
    def from_int(cls, value: int):
        if value >= LogClickLevel.DEBUG:
            return LogClickLevel.DEBUG
        if value <= LogClickLevel.FATAL:
            return LogClickLevel.FATAL
        return LogClickLevel(value)


_LOG_LEVEL = LogClickLevel.WARNING


def set_loglevel(level: LogClickLevel):
    global _LOG_LEVEL
    _LOG_LEVEL = level

def get_loglevel() -> LogClickLevel:
    return _LOG_LEVEL

def _log_common(text: str, level: LogClickLevel):
    if get_loglevel() >= level:
        click.echo(f'[{level.name}]: {text}')

def debug(text: str):
    _log_common(text, LogClickLevel.DEBUG)

def command(text: str):
    _log_common(text, LogClickLevel.CMD)

def subcommand(text: str):
    _log_common(text, LogClickLevel.SUBCMD)

def info(text: str):
    _log_common(text, LogClickLevel.INFO)

def warn(text: str):
    _log_common(text, LogClickLevel.WARNING)

def error(text: str):
    _log_common(text, LogClickLevel.ERROR)

def fatal(text: str):
    _log_common(text, LogClickLevel.FATAL)