# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : field.py
# Date   : 2017-03-13 15-23
# Version: 0.0.1
# Description: description of this file.

import datetime

from dataobj.exception import FieldFormatError

__version__ = '0.0.1'
__author__ = 'Chris'


class Field(object):
    type = str

    def __init__(self, db_column=None, default=None, primary_key=False):
        self.name = None
        self._db_column = db_column
        self._default = default
        self.primary_key = primary_key

    @property
    def default_value(self):
        try:
            return self._default()
        except:
            return self._default

    @property
    def db_column(self):
        return self._db_column or self.name

    def __str__(self):
        return 'name={}, column={}'.format(self.name, self.db_column)

    def db_format(self, value):
        try:
            if value is None:
                return value

            assert isinstance(value, self.type)
            return self._db_format(value)
        except:
            raise FieldFormatError(
                'Column `{}` expected type `{}`, not `{}`: {}'.format(self.db_column, self.type, type(value), value))

    def output_format(self, value):
        return self._output_format(value)

    def _db_format(self, value):
        raise NotImplementedError

    def _output_format(self, value):
        return value


class IntField(Field):
    type = int

    def _db_format(self, value):
        return '{}'.format(int(value))


class StrField(Field):
    type = str

    def _db_format(self, value):
        return '{}'.format(value)


class DatetimeField(Field):
    type = datetime.datetime

    def _db_format(self, value):
        return '{}'.format(value.isoformat())


class DateField(Field):
    type = datetime.date

    def _db_format(self, value):
        return '{}'.format(value.isoformat())


class TimeField(Field):
    type = datetime.time

    def _db_format(self, value):
        return '{}'.format(value.isoformat())


class BoolField(Field):
    type = bool

    def _db_format(self, value):
        return 1 if value is True else 0

    def _output_format(self, value):
        return bool(value)


class FloatField(Field):
    type = float

    def _db_format(self, value):
        return '{}'.format(value)


if __name__ == '__main__':
    f = BoolField()
    print(f.db_format(False))
    # print(f.output_format(100))
