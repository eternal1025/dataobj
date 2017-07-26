# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: MIT License
# File   : test_pydatetime_converter.py
# Date   : 2017-07-26 14-03
# Version: 0.1
# Description: description of this file.

import pytest
import datetime
import pandas as pd


@pytest.mark.parametrize('tm, wanted',
                         [
                             ("2018-08-08", datetime.datetime(year=2018, month=8, day=8)),
                             ("2018-08-08 01:02:03",
                              datetime.datetime(year=2018, month=8, day=8, hour=1, minute=2, second=3)),
                             ("10:20", datetime.datetime.now().replace(hour=10, minute=20, second=0, microsecond=0)),
                             ("10:20:30",
                              datetime.datetime.now().replace(hour=10, minute=20, second=30, microsecond=0)),
                             (datetime.datetime(year=2018, month=8, day=20),
                              datetime.datetime(year=2018, month=8, day=20)),
                             (datetime.date(year=2018, month=8, day=20), datetime.datetime(year=2018, month=8, day=20)),
                             (pd.tslib.Timestamp(year=2018, month=8, day=20),
                              datetime.datetime(year=2018, month=8, day=20))
                         ], ids=["date string", "datetime string", "time string", "full time string",
                                 "datetime type", "date type", "pandas Timestamp type"])
def test_convert_to_datetime_ok(converter, tm, wanted):
    got = converter.convert(tm, 'datetime')
    assert isinstance(got, datetime.datetime)
    assert got == wanted


@pytest.mark.parametrize('tm, wanted',
                         [
                             ("2018-08-08", datetime.date(year=2018, month=8, day=8)),
                             ("2018-08-08 10:20:30", datetime.date(year=2018, month=8, day=8)),
                             ("10:20", datetime.datetime.now().date()),
                             ("10:20:50", datetime.datetime.now().date()),
                             (datetime.date(year=2018, month=8, day=8), datetime.date(year=2018, month=8, day=8)),
                             (datetime.datetime(year=2018, month=8, day=8), datetime.date(year=2018, month=8, day=8)),
                             (datetime.datetime.now(), datetime.datetime.now().date()),
                             (pd.tslib.Timestamp(year=2018, month=8, day=20),
                              datetime.date(year=2018, month=8, day=20))
                         ], ids=["date string", "datetime string", "time string", "full time string",
                                 "date type", 'datetime type', 'datetime.now',
                                 'pandas Timestamp type'])
def test_convert_to_date_ok(converter, tm, wanted):
    got = converter.convert(tm, 'date')
    assert isinstance(got, datetime.date)
    assert got == wanted


@pytest.mark.parametrize('tm, wanted',
                         [
                             ("10:20", datetime.time(hour=10, minute=20)),
                             ("10:20:40", datetime.time(hour=10, minute=20, second=40)),
                             (datetime.time(hour=10, minute=10), datetime.time(hour=10, minute=10)),
                             (datetime.datetime.now().replace(microsecond=0),
                              datetime.datetime.now().time().replace(microsecond=0)),
                             (pd.tslib.Timestamp(year=2018, month=8, day=20, hour=20, minute=20, second=20),
                              datetime.time(hour=20, minute=20, second=20)),
                         ], ids=['time string', 'full time string', 'time type',
                                 'datetime.now', 'pandas Timestamp'])
def test_convert_to_time_ok(converter, tm, wanted):
    got = converter.convert(tm, 'time')
    assert isinstance(got, datetime.time)
    assert got == wanted


@pytest.mark.parametrize('tp',
                         [
                             'foo',
                             'bar'
                         ])
def test_convert_failed_invalid_conversion_type(converter, tp):
    with pytest.raises(ValueError):
        converter.convert("2012-12-12", tp)


@pytest.mark.parametrize('tm',
                         [
                             '2012-13-12',
                             '2012-00-01',
                             '27:34'
                         ])
def test_convert_failed_invalid_time_format_etc(converter, tm):
    with pytest.raises(ValueError):
        converter.convert(tm, 'datetime')
