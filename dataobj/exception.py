# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : exception.py
# Date   : 2017-03-13 16-47
# Version: 0.0.1
# Description: description of this file.


__version__ = '0.0.1'
__author__ = 'Chris'


class FieldFormatError(Exception):
    pass


class TableNotDefinedError(Exception):
    pass


class DuplicatePrimaryKeyError(Exception):
    pass


class PrimaryKeyNotFoundError(Exception):
    pass


class UnknownColumnError(Exception):
    pass
