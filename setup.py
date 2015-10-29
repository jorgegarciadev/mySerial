#!/usr/bin/env python
# coding: UTF-8

from setuptools import setup, find_packages


version = '0.6.1'

setup(
    name='myserial',
    version=version,
    description='urwid based serial monitor.',
    author='Jorge García',
    author_email='jorgegarciadev@icloud.com',
    license='MIT',
    keywords=['serial', 'uart', 'monitor', 'command line', 'cli', 'websockets'],
    url='https://github.com/jorgegarciadev/mySerial',
    packages=find_packages(),
    install_requires=[
        'backports.ssl-match-hostname>=3.4.0.2',
        'pyserial>=2.7',
        'urwid>=1.3.0',
        'websocket-client>=0.32.0'
    ],
    entry_points={
        'console_scripts': [
            'myserial=myserial.myserial:main'
        ],
    }
)
