# -*- coding:utf-8 -*-
from setuptools import find_packages, setup
import os

setup(
    name='osc-tui',
    version="22.9.0",
    packages=find_packages(),
    author='Outscale SAS',
    author_email='opensource@outscale.com',
    description='Outscale',
    url='http://www.outscale.com/',
    entry_points={'console_scripts': ['osc-tui = osc_tui.main:main']},
    install_requires=[
        'setuptools',
        'requests'
    ],
)
