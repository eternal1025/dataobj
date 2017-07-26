# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : test_fields.py
# Date   : 2017-05-16 11-39
# Version: 0.0.1
# Description: description of this file.

import datetime

import pandas as pd

from dataobj.fields import *

__version__ = '0.0.1'
__author__ = 'Chris'


def test_int_field():
    int_field = IntField(primary_key=True,
                         choices=[100, 200])
    int_field.field_name = 'int_field'

    print(int_field.db_column)
    print(int_field.validators)

    print(int_field.validate_input('100'))
    print(int_field.validate_output(100))


def test_float_field():
    field = FloatField(db_column='float_field',
                       primary_key=False,
                       default=100.2)
    field.field_name = 'float_field'
    print(field.validate_input('1002.3'))
    print(field.validate_input(100 / 2))


def test_decimal_field():
    field = DecimalField(db_column='decimal',
                         primary_key=False,
                         default=lambda: 100 * 2.3)
    field.field_name = 'decimal'
    print(field.default)
    print(field.validate_input(100.2))


def test_str_field():
    field = StrField(db_column='str',
                     max_length=10)
    field.field_name = 'str'
    print(field.validate_input('Hello'))


def test_blob_field():
    field = BlobField(db_column='blob', min_length=1)
    field.field_name = 'blob'
    print(field.validate_input(b'test'))


def test_date_field():
    field = DateField(db_column='date')
    field.field_name = 'date'
    print(field.validate_input('2014-09-08'))
    print(field.validate_input('2014-09-08 12:23:09'))
    print(field.validate_input(datetime.datetime.now()))
    print(field.validate_input(datetime.datetime.now().time()))


def test_datetime_field():
    field = DatetimeField(db_column='datetime')
    field.field_name = 'datetime'
    print(field.validate_input('2017-05-16'))
    print(field.validate_input('2017-05-16 09:00'))
    print(field.validate_input(pd.Timedelta(hours=10, minutes=10)))


def test_time_field():
    field = TimeField(db_column='time')
    field.field_name = 'time'
    print(field.validate_input('0 days 03:00:23'))
    print(field.validate_input(datetime.datetime.now()))
    print(field.validate_input('09:20:20'))


def test_bool_field():
    field = BoolField(db_column='bool')
    field.field_name = 'bool'
    print(field.validate_input(False))
    print(field.validate_output(0))


def test_list_field():
    field = ListField(db_column='list', not_null=False,
                      json_dumps_default=lambda v: str(v))
    field.field_name = 'list'
    x = field.validate_input((1, 2, 3, 4, '2010', datetime.datetime.now()))
    print(x, type(x))
    print(field.validate_output(x))


def test_dict_field():
    field = DictField(db_column='dict')
    field.field_name = 'dict'
    x = field.validate_input({"1": 1, '2': 2})
    print(x)
    print(field.validate_output(x))


class Person(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


def test_pickle_field():
    field = PickleField(db_column='pickle')
    field.field_name = 'pickle'
    x = field.validate_input(Person('Chris'))
    print(x)
    print(field.validate_output(x))


if __name__ == '__main__':
    test_int_field()
    test_float_field()
    test_decimal_field()
    test_str_field()
    test_blob_field()
    test_date_field()
    test_datetime_field()
    test_time_field()
    test_bool_field()
    test_list_field()
    test_dict_field()
    test_pickle_field()
    print(DatetimeField(default=lambda: datetime.datetime.now).default)
