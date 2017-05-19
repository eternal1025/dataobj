# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : utils.py
# Date   : 2017-05-16 15-11
# Version: 0.0.1
# Description: description of this file.

import hashlib
import pickle
import warnings
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


def underscore_to_camel(key):
    return ''.join(x.capitalize() for x in key.split('_'))


def get_object_fingerprint(obj, hash_method='md5'):
    """
    Generate a unique fingerprint for the given object

    :return: hash value
    """
    method = getattr(hashlib, hash_method)
    return method(pickle.dumps(obj)).hexdigest()


def validate_dao_class(c):
    """
    Check the dao class is valid or not

    Raise error if not acceptable
    """
    if c is None:
        raise RuntimeError("Fatal error, missing dao class")

    query = getattr(c, "query", None)

    if query is None or callable(query) is False:
        raise RuntimeError('Class "{}" must implements the method "query(sql, args)"'.format(c.__name__))

    execute = getattr(c, 'execute', None)

    if execute is None or callable(execute) is False:
        warnings.warn('Method "execute(sql, args)" is not implemented in class "{}", thus, '
                      '"model.dump", "model.update" and "model.delete" will have no effects '
                      'when you call these methods.'.format(c.__name__))


if __name__ == '__main__':
    x = underscore_to_camel("hello_test")
    print(x)
