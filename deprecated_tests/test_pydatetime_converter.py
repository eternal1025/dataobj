# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : test_pydatetime_converter.py
# Date   : 2017-05-16 11-39
# Version: 0.0.1
# Description: description of this file.

import pandas as pd

import datetime

from dataobj.converters import PyDatetimeConverter

__version__ = '0.0.1'
__author__ = 'Chris'

if __name__ == '__main__':
    c = PyDatetimeConverter()
    print(c.convert('2017-09-08', 'date'))
    print(c.convert('2017-05-16 12:12:12'))
    print(c.convert('2017-05-16 12:12:12', 'time'))
    print(c.convert('2017-05-16 12:12:12', 'date'))
    print(c.convert('2017-05-16 12:12:12', 'date'))
    print(c.convert(datetime.datetime.now(), 'time'))
    print(c.convert(datetime.datetime.now(), 'date'))
    print(c.convert(datetime.datetime.now().time(), 'date'))
    print(c.convert(datetime.datetime.now().date(), 'datetime'))
    print(c.convert('0 days 12:00:30', 'time'))
    print(c.convert(pd.Timedelta(hours=20, minutes=29), 'time'))
    print(c.convert(pd.Timestamp(year=2017, month=5, day=16), 'date'))
