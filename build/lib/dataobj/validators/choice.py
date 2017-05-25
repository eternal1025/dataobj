# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : choice.py
# Date   : 2017-05-12 16-06
# Version: 0.0.1
# Description: description of this file.


__version__ = '0.0.1'
__author__ = 'Chris'


class ChoiceValidator(object):
    def __init__(self, choices=None, error_handler=None):
        self._choices = choices or []
        self._error_handler = error_handler

    def __repr__(self):
        return '<ChoiceValidator choices={}>'.format(self._choices)

    def validate(self, param, value):
        if value is None:
            return value

        if value in self._choices:
            return value

        if self._error_handler and callable(self._error_handler):
            return self._error_handler(value)

        raise ValueError('Choice validation error on param `{}={}`, '
                         'available choices are `{}`'.format(param, value, self._choices))
