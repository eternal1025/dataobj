# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : length.py
# Date   : 2017-05-12 15-34
# Version: 0.0.1
# Description: description of this file.


__version__ = '0.0.1'
__author__ = 'Chris'


class LengthValidator(object):
    def __init__(self, min_length=None, max_length=None, error_handler=None):
        self._min_length = min_length or 0
        self._max_length = max_length or float('inf')
        self._error_handler = error_handler

    def __repr__(self):
        return '<LengthValidator min_len={}, max_len={}>'.format(self._min_length,
                                                                 self._max_length)

    def validate(self, param, value):
        if value is None:
            return value

        length = len(value)
        if self._min_length <= length <= self._max_length:
            return value

        if self._error_handler and callable(self._error_handler):
            return self._error_handler(value)

        raise ValueError('Length validation error on param `{}={}`, '
                         'range of length is ({}, {})'.format(param, value,
                                                              self._min_length,
                                                              self._max_length))


if __name__ == '__main__':
    v = LengthValidator(1, 3, error_handler=lambda x: x[:3])
    print(v.validate('test', [1, 2, 3, 4]))
