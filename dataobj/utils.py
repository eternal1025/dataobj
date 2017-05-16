# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : utils.py
# Date   : 2017-05-16 15-11
# Version: 0.0.1
# Description: description of this file.

from string import ascii_uppercase, ascii_lowercase

__version__ = '0.0.1'
__author__ = 'Chris'

ASCII_MAPPING = dict((k, '_{}'.format(v)) for k, v in zip(ascii_uppercase, ascii_lowercase))


def camel_to_underscore(key):
    """
    Fast way to converse camel style to underscore style
    :param key: word to be converted
    :return: str
    """
    return ''.join(ASCII_MAPPING.get(x) or x for x in key).strip('_')
