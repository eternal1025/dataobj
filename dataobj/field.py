# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : field.py
# Date   : 2017-03-13 15-23
# Version: 0.0.1
# Description: description of this file.

import datetime
import json

from dataobj.exception import FieldFormatError
from pymysql.converters import (escape_float, escape_int, escape_bool,
                                escape_datetime, escape_date,
                                escape_str, escape_time, escape_bytes)
from decimal import Decimal

__version__ = '0.0.1'
__author__ = 'Chris'


class Field(object):
    type = str

    def __init__(self, db_column=None, default=None, primary_key=False):
        self.name = None
        self._db_column = db_column
        self.default = default
        self.primary_key = primary_key

    @property
    def default_value(self):
        try:
            return self.default()
        except:
            return self.default

    @property
    def db_column(self):
        return self._db_column or self.name

    def __str__(self):
        return 'name={}, column={}'.format(self.name, self.db_column)

    def db_format(self, value):
        try:
            if value is None:
                return value

            if isinstance(value, self.type) is False:
                raise FieldFormatError(
                    'Column `{}` expected type `{}`, not `{}`: {}'.format(self.db_column, self.type, type(value),
                                                                          value))

            return self._db_format(value).replace('\'', '')
        except Exception:
            raise

    def output_format(self, value):
        return self._output_format(value)

    def _db_format(self, value):
        raise NotImplementedError

    def _output_format(self, value):
        return value


class BlobField(Field):
    type = (bytes,)

    def _db_format(self, value):
        return escape_bytes(value)

    def _output_format(self, value):
        return value


class IntField(Field):
    type = (int, float)

    def _db_format(self, value):
        return escape_int(value)

    def _output_format(self, value):
        try:
            return int(value)
        except:
            return None


class StrField(Field):
    type = str

    def _db_format(self, value):
        return escape_str(value)


class DatetimeField(Field):
    type = datetime.datetime

    def _db_format(self, value):
        return escape_datetime(value)

    def _output_format(self, value):
        return value


class DateField(Field):
    type = (datetime.date, datetime.datetime)

    def _db_format(self, value):
        return escape_date(value)


class TimeField(Field):
    type = (datetime.datetime, datetime.time)

    def _db_format(self, value):
        return escape_time(value)


class BoolField(Field):
    type = bool

    def _db_format(self, value):
        return escape_bool(value)

    def _output_format(self, value):
        return bool(value)


class FloatField(Field):
    type = (float, int)

    def _db_format(self, value):
        return escape_float(value)

    def _output_format(self, value):
        try:
            return float(value)
        except:
            return None


class DecimalField(Field):
    type = (Decimal, int, float)

    def _db_format(self, value):
        return '{}'.format(value)

    def _output_format(self, value):
        return value


class _BasicCollectionField(Field):
    def _db_format(self, value):
        try:
            return escape_str(json.dumps(value))
        except:
            return value

    def _output_format(self, value):
        try:
            return json.loads(value)
        except:
            return value


class ListField(_BasicCollectionField):
    type = list


class DictField(_BasicCollectionField):
    type = dict


class SetField(_BasicCollectionField):
    type = set


class PickleField(Field):
    type = object

    def _db_format(self, value):
        s = self.__encode(value)
        return s

    def _output_format(self, value):
        return self.__decode(value)

    @staticmethod
    def __encode(value):
        import base64
        import pickle

        try:
            return (base64.encodebytes(pickle.dumps(value)).decode()).strip()
        except pickle.PicklingError:
            pass

    @staticmethod
    def __decode(value):
        import base64
        import pickle

        if value is None:
            return None

        try:
            return pickle.loads(base64.decodebytes(value.strip().encode()))
        except pickle.PicklingError:
            pass


if __name__ == '__main__':
    from datetime import datetime

    d = FloatField()
    # d = DatetimeField()
    o = d.db_format(2.336)
    print(o)
