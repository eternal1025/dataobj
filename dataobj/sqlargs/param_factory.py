# -*-coding: utf-8-*-
# Author : XiaoLiFeiDao
# License: Apache License
# File   : param_factory.py
# Date   : 2017-02-27 11-05
# Version: 0.0.1
# Description: simple param factories


__version__ = '0.0.1'
__author__ = 'Chris'

__all__ = ['ParamFactory']


class ParamFactory(object):
    def __init__(self, *args, **kwargs):
        self._params = kwargs if len(kwargs) > 0 else args

    def _equal_dict(self):
        params = []

        try:
            for key, value in self._params.items():
                if isinstance(value, int):
                    params.append('{} = {}'.format(key, value))
                elif str(value).upper == 'NULL':
                    params.append('{} IS NULL'.format(key))
                elif not value:
                    params.append('{} = NULL'.format(key))
                else:
                    params.append('{} = "{}"'.format(key, value))
        except Exception as err:
            print(err)
        else:
            return params

    def _equal_list(self):
        params = []

        try:
            for key in self._params:
                params.append('{} = %s'.format(key))
        except Exception as err:
            print(err)
        else:
            return params

    def _sep_dict(self):
        keys = []
        values = []

        try:
            for key, value in self._params.items():
                keys.append(key)
                if isinstance(value, int):
                    values.append('{}'.format(value))
                elif value is None:
                    values.append('NULL')
                else:
                    values.append('"{}"'.format(value))
        except Exception as err:
            print(err)
        else:
            return keys, values

    def _sep_list(self):
        keys = []
        values = []

        try:
            for key in self._params:
                keys.append(str(key))
                values.append('%s')
        except Exception as err:
            print(err)
        else:
            return keys, values


class OnlyKeys(ParamFactory):
    @property
    def params(self):
        return tuple(self._params) if isinstance(self._params, (str, list, tuple)) else self._sep_list()[0]


class KeyValuesSep(ParamFactory):
    @property
    def params(self):
        return self._sep_dict() if isinstance(self._params, dict) else self._sep_list()


class KeyValuesEqual(ParamFactory):
    @property
    def params(self):
        return self._equal_dict() if isinstance(self._params, dict) else self._equal_list()
