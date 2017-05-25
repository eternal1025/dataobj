# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : qq.py
# Date   : 2017-05-12 16-31
# Version: 0.0.1
# Description: description of this file.


import re

__version__ = '0.0.1'
__author__ = 'Chris'


class QQNumberValidator(object):
    def __init__(self, error_handler=None):
        self._error_handler = error_handler

    def __repr__(self):
        return '<QQNumberValidator>'

    def validate(self, param, value):
        if value is None:
            return value

        pattern = '[1-9][0-9]{4,}'

        if re.match(pattern, value):
            return value

        if self._error_handler and callable(self._error_handler):
            return self._error_handler(value)

        raise ValueError('QQ number validation error on param `{}={}`'.format(param, value))


if __name__ == '__main__':
    v = QQNumberValidator()
    print(v.validate('qq', 'abc1929911'))
