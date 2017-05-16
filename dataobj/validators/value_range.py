# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : value_range.py
# Date   : 2017-05-12 16-55
# Version: 0.0.1
# Description: description of this file.


__version__ = '0.0.1'
__author__ = 'Chris'


class ValueRangeValidator(object):
    def __init__(self, min_value, max_value, error_handler=None):
        self._error_handler = error_handler
        self._min_value = min_value
        self._max_value = max_value

    def __repr__(self):
        return '<ValueRangeValidator min_value={}, max_value={}>'.format(self._min_value,
                                                                         self._max_value)

    def validate(self, param, value):
        if value is None:
            return value

        if self._min_value <= value <= self._max_value:
            return value

        if self._error_handler and callable(self._error_handler):
            return self._error_handler

        raise ValueError('Value range validation error on param `{}={}`'.format(param, value))
