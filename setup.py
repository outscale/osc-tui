# -*- coding:utf-8 -*-
import os
from setuptools import find_packages, setup

def get_long_description():
    root_path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(root_path, 'README.md'), 'r') as fd:
        return fd.read()


setup(
    name='osc-tui',
    version="25.03.0",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
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
        "graphviz",
        'requests'
    ],
)
