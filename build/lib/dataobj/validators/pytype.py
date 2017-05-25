# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : basic.py
# Date   : 2017-05-12 13-40
# Version: 0.0.1
# Description: description of this file.

__version__ = '0.0.1'
__author__ = 'Chris'


class TypeValidator(object):
    def __init__(self, expected_type, force_converse_handler=None,
                 error_handler=None):
        self._expected_type = expected_type
        self._force_converse_handler = force_converse_handler
        self._error_handler = error_handler or force_converse_handler

    def __repr__(self):
        return '<TypeValidator expected_type={}>'.format(self._expected_type)

    def validate(self, param, value):
        if value is None:
            return value

        try:
            if self._force_converse_handler and callable(self._force_converse_handler):
                return self._force_converse_handler(value)
            else:
                return self.converse(value)
        except Exception:
            if self._error_handler and callable(self._error_handler):
                return self._error_handler(value)

        raise TypeError('Type validation error on param `{}={}`,'
                        ' expected type `{}`, got type `{}`'.format(param, value, self._expected_type, type(value)))

    def converse(self, value):
        if isinstance(value, self._expected_type):
            return value

        return self._expected_type(value)


if __name__ == '__main__':
    v = TypeValidator(int)
    print(v.validate(1200))

    v = TypeValidator(list)
    print(v.validate(0))
