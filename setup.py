from setuptools import setup

import pman.build_apps

CONFIG = pman.get_config()

APP_NAME = CONFIG['general']['name']

setup(
    name=APP_NAME,
    version='1.0.1',
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pylint',
        'pytest-pylint',
    ],
    cmdclass={
        'build_apps': pman.build_apps.BuildApps,
    },
    options={
        'build_apps': {
            'include_patterns': {
                'game/**',
                '.pman',
                'settings.prc',
                'levels/*.lvl',
                'README.md',
            },
            'exclude_patterns': {
                '*.py',
                '**/*.py',
            },
            'rename_paths': {
                'game/': './',
            },
            'gui_apps': {
                APP_NAME: CONFIG['run']['main_file'],
            },
            'log_filename': '$USER_APPDATA/hexima/output.log',
            'log_append': False,
            'plugins': [
                'pandagl',
                'p3openal_audio',
                'p3fmod_audio',
            ],
        },
    }
)
