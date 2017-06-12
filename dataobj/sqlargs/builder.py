# -*-coding: utf-8-*-
# Author : XiaoLiFeiDao
# License: Apache License
# File   : builder.py
# Date   : 2017-02-27 11-05
# Version: 0.0.1
# Description: simple sql builder.
from pprint import pformat

from dataobj.sqlargs.sql_factory import SQLArgsFactory

__version__ = '0.0.1'
__author__ = 'Chris'

__all__ = ['SQLArgsBuilder']


class SQLArgsBuilder(object):
    queries = ('select', 'insert', 'update', 'delete',
               'where', 'group_by', 'having',
               'descending_order_by', 'ascending_order_by', 'limit')

    def __init__(self, table, **kwargs):
        self._table = table
        self._kwargs = kwargs

    def __repr__(self):
        return pformat('<SQLArgsBuilder sql={}, args={}>'.format(*self.sql_args))

    def _combine_factories(self):
        for key, value in self._kwargs.items():
            try:
                if isinstance(value, str):
                    value = value.split(',')
                    value = [x.strip() for x in value if x.strip()]
                else:
                    iter(value)
            except TypeError:
                value = [value]

            if isinstance(value, dict):
                yield key, SQLArgsFactory(self._table, key, **value)
            else:
                yield key, SQLArgsFactory(self._table, key, *value)

    def _build_sql_args(self):
        factories = dict(self._combine_factories())

        for q in self.queries:
            try:
                factory = factories.get(q)
                if factory:
                    yield factory.sql_args
            except KeyError:
                print('Unsupported _query: {}'.format(q))

    @property
    def sql_args(self):
        sql_parts = []
        full_args = dict()

        for sql, args in self._build_sql_args():
            sql_parts.append(sql)
            full_args.update(args)

        return ''.join(sql_parts).strip(), full_args


if __name__ == '__main__':
    f = ['name', 'age', 'country']
    data = {
        'name': 'chris',
        'age': 24,
        'country': 'China',
        'city': 'Beijing'
    }

    condition = {
        'name__startswith': 'c'
    }

    builder = SQLArgsBuilder('test', select=data, where=condition, descending_order_by='xyz', limit=(1, 10))
    print(builder)
