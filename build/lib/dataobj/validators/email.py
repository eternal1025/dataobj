# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : email.py
# Date   : 2017-05-12 16-14
# Version: 0.0.1
# Description: description of this file.

import re

__version__ = '0.0.1'
__author__ = 'Chris'


class EmailValidator(object):
    def __init__(self, error_handler=None):
        self._error_handler = error_handler

    def __repr__(self):
        return '<EmailValidator>'

    def validate(self, param, value):
        if value is None:
            return value

        pattern = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'
        if re.match(pattern, value):
            return value

        if self._error_handler and callable(self._error_handler):
            return self._error_handler(value)

        raise ValueError('Email validation error on param `{}={}`'.format(param, value))


if __name__ == '__main__':
    v = EmailValidator(None)
    print(v.validate('email', 'mail@chriscabin.com'))
