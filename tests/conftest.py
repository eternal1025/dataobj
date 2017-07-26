# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: MIT License
# File   : conftest.py
# Date   : 2017-07-26 14-06
# Version: 0.1
# Description: description of this file.

import pytest


@pytest.fixture(scope='module')
def converter():
    from dataobj.converters import PyDatetimeConverter
    return PyDatetimeConverter()
