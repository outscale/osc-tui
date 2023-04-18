# -*- coding:utf-8 -*-
from setuptools import find_packages, setup
import os

setup(
    name='osc-tui',
    version="23.03.0",
    packages=find_packages(),
    author='Outscale SAS',
    author_email='opensource@outscale.com',
    description='Outscale',
    url='http://www.outscale.com/',
    entry_points={'console_scripts': ['osc-tui = osc_tui.main:main']},
    install_requires=[
        'setuptools',
        "requests>=2.28.1",
        "osc-sdk-python>=0.22.0",
        "pyperclip>=1.8.0",
        'oscscreen @ git+https://github.com/outscale/npyscreen.git@master#egg=oscscreen',
        'requests'
    ],
)
