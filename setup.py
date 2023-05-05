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
        #"osc-sdk-python>=0.22.0",
        "pyperclip>=1.8.0",
        'osc_diagram @ git+https://github.com/outscale-mgo/osc-diagram@master#egg=osc_diagram',
        'oscscreen @ git+https://github.com/outscale/npyscreen.git@master',
        "osc-sdk-python @ git+https://github.com/outscale/osc-sdk-python.git@master",
        'requests'
    ],
)
