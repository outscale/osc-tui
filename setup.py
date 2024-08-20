# -*- coding:utf-8 -*-
from setuptools import find_packages, setup

setup(
    name='osc-tui',
    version="24.06.0",
    packages=find_packages(),
    author='Outscale SAS',
    author_email='opensource@outscale.com',
    description='Outscale',
    url='http://www.outscale.com/',
    entry_points={'console_scripts': ['osc-tui = osc_tui.main:main']},
    install_requires=[
        'setuptools',
        "requests>=2.28.1",
        "osc-sdk-python>=0.26.0",
        "pyperclip>=1.8.0",
        'osc_diagram',
        'osc_npyscreen',
        'requests'
    ],
)
