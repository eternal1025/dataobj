# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : converters.py
# Date   : 2017-05-16 10-56
# Version: 0.0.1
# Description: description of this file.

import pandas as pd
import datetime

from dateutil import parser

__version__ = '0.0.1'
__author__ = 'Chris'


class PyDatetimeConverter(object):
    """
    Try to convert any given time to python datetime.

    Output can be datetime.date, datetime.datetime, datetime.time
    """

    def __init__(self, info=None):
        self._info = info

    def convert(self, tm, to_what='datetime'):
        """
        Convert any given time to the specified `to_what` type

        :param tm: str or datetime.time, datetime.date
        :param to_what: str, choices: date, datetime, time
        :return: default is `datetime.datetime` type
        """
        if tm is None:
            return tm

        if isinstance(tm, datetime.datetime):
            return self._to_what_kind(tm, to_what)

        converter = {
            str: self._str_to_pydatetime,
            datetime.date: self._pydate_to_pydatetime,
            datetime.time: self._pytime_to_pydatetime,
            datetime.timedelta: self._pytimedelta_to_pydatetime,
            pd.Timedelta: self._pdtimedelta_to_pydatetime,
            pd.Timestamp: self._pdtimestamp_to_pydatetime
        }.get(type(tm))

        if converter and callable(converter):
            return self._to_what_kind(converter(tm), to_what)
        else:
            raise ValueError('Unsupported type for PyDateTimeConverter: {}({})'.format(tm,
                                                                                       type(tm)))

    @staticmethod
    def _to_what_kind(dt, to_what):
        factory = {
            'date': dt.date,
            'datetime': dt,
            'time': dt.time
        }.get(to_what)

        if factory is None:
            raise ValueError('Unsupported datetime factory: {}, '
                             'choices are `date`, `datetime`, `time`'.format(to_what))

        if callable(factory):
            return factory()

        return factory

    def _str_to_pydatetime(self, s):
        if 'days' in s:
            return self._pdtimedelta_to_pydatetime(pd.to_timedelta(s))
        else:
            return parser.parse(s)

    @staticmethod
    def _pydate_to_pydatetime(s):
        return datetime.datetime(year=s.year,
                                 month=s.month,
                                 day=s.day)

    @staticmethod
    def _pytime_to_pydatetime(s):
        now = datetime.datetime.now()
        return datetime.datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=s.hour,
            minute=s.minute,
            second=s.second,
            microsecond=s.microsecond
        )

    @staticmethod
    def _pytimedelta_to_pydatetime(s):
        now = datetime.datetime.now()
        future = datetime.datetime(year=now.year, month=now.month,
                                   day=now.day) + s
        return future

    @staticmethod
    def _pdtimedelta_to_pydatetime(s):
        today = datetime.datetime.now()
        return datetime.datetime(year=today.year,
                                 month=today.month,
                                 day=today.day,
                                 hour=s.components.hours,
                                 minute=s.components.minutes,
                                 second=s.components.seconds)

    @staticmethod
    def _pdtimestamp_to_pydatetime(s):
        return s.to_pydatetime()


__all__ = ['PyDatetimeConverter']
