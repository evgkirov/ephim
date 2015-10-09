import sys

from setuptools import setup

PY_VERSION = sys.version_info[0], sys.version_info[1]

setup(
    name='ephim',
    packages=['ephim'],
    entry_points={
        'console_scripts': [
            'ephim = ephim.cli:main',
        ],
    },
    install_requires=list(filter(None, open('requirements.txt', 'r').read().split('\n'))),
)
