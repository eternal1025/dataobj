# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : phone.py
# Date   : 2017-05-12 16-24
# Version: 0.0.1
# Description: description of this file.

import re

__version__ = '0.0.1'
__author__ = 'Chris'


class PhoneNumberValidator(object):
    def __init__(self, error_handler=None):
        self._error_handler = error_handler

    def __repr__(self):
        return '<PhoneNumberValidator>'

    def validate(self, param, value):
        if value is None:
            return value

        pattern = r'0?(13|14|15|18)[0-9]{9}'

        if re.match(pattern, value):
            return value

        if self._error_handler and callable(self._error_handler):
            return self._error_handler(value)

        raise ValueError('Phone number validation error on param `{}={}`'.format(param, value))


if __name__ == '__main__':
    v = PhoneNumberValidator()
    print(v.validate('phone', '18801444657'))
