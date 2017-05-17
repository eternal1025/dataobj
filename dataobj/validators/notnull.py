# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : null.py
# Date   : 2017-05-12 15-50
# Version: 0.0.1
# Description: description of this file.

__version__ = '0.0.1'
__author__ = 'Chris'


class NotNullValidator(object):
    def __init__(self, error_handler=None):
        self._error_handler = error_handler

    def __repr__(self):
        return '<NotNullValidator>'

    def validate(self, param, value):
        # if isinstance(value, (int, float)):
        #     return value
        # Empty list(or dict, set etc..) is not NULL, just empty.
        return value if value is not None else self._error(param, value)

    def _error(self, param, value):
        if self._error_handler and callable(self._error_handler):
            return self._error_handler(value)

        raise ValueError('Not null validation error on param `{}={}`'.format(param, value))
