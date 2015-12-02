# -*- coding: utf-8 -*-
__author__ = 'banxi'
from setuptools import setup

setup(
    name='XcodeMediaTools',
    version='0.1.2',
    author='Haizhen Lee',
    author_email='banxi1988@gmail.com',
    description='Xcode Media Tools',
    install_requires=['click'],
    py_modules=['xmt'],
    package_data={
        '': ['*.json']
    },
    entry_points={
        'console_scripts': [
            'xmt=xmt:main'
        ]
    },
    license='MIT'
)
