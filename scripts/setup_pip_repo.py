#!/usr/bin/env python3
"""
using the output from `gcloud artifacts print-settings`, configure pip and
twine for the gcloud repo
"""

from argparse import ArgumentParser
from configparser import ConfigParser
from enum import Enum
from pathlib import Path
import subprocess

PYPIRC = Path().home().joinpath('.pypirc')
DOT_CONF_KEYS = frozenset(['global'])


class CONF_LEVEL(Enum):
    SITE = '--local'
    USER = '--user'
    GLOBAL = '--global'


def _update_pypirc(**new_config: dict) -> None:
    """
    Update a ~.pypirc (or create if nonexistent) to include configuration
    passed in.

    Args:
        * new_config: freeform kwargs, with names of strings mapping to config
                      parser sections
    """

    pypirc = ConfigParser()
    pypirc.read(PYPIRC)

    pypirc.update(new_config)

    with PYPIRC.open('w') as fh:
        pypirc.write(fh)

    return pypirc


def _update_pip_dot_conf(index_url: str, level=CONF_LEVEL.SITE) -> None:

    subprocess.check_call(['git', 'config', level.value, 'global.extra-index-url', index_url])


def main():
    """
    Main UI loop for use as a script
    """

    parser = ArgumentParser()
    parser.add_argument('--repository', '--repo', '-r', default='python')
    parsed = parser.parse_args()
    conf_res = subprocess.check_output(
        ['gcloud', 'artifacts', 'print-settings',
         'python', '--repository', parsed.repository])

    conf = ConfigParser()
    conf.read_string(conf_res.decode())

    _update_pypirc(**dict((k, v) for k, v in conf.items() if k not in DOT_CONF_KEYS))

    _update_pip_dot_conf(conf['global']['extra-index-url'])


if __name__ == '__main__':
    main()
