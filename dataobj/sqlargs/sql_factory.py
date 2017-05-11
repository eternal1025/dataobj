# -*-coding: utf-8-*-
# Author : XiaoLiFeiDao
# License: Apache License
# File   : query_factory.py
# Date   : 2017-02-27 11-05
# Version: 0.0.1
# Description: simple sql factories


from dataobj.sqlargs.condition_parser import ConditionParser

__version__ = '0.0.2'
__author__ = 'Chris'

__all__ = ['SQLArgsFactory']


class SQLArgsFactory(object):
    def __init__(self, table, query, *args, **kwargs):
        self._table = table
        self._query = query.lower()
        self._args = args
        self._kwargs = kwargs

    def __repr__(self):
        return '<sql={}, args={}>'.format(*self.sql_args)

    @property
    def sql_args(self):
        result = getattr(self, '_' + self._query)()
        if not result:
            return '', {}
        else:
            return result

    @property
    def fields(self):
        return self._args or self._kwargs

    def _select(self):
        sql = 'SELECT {fields} FROM {table}'
        fields = ', '.join(self.fields or ['*'])
        return sql.format(fields=fields, table=self._table), {}

    def _insert(self):
        if self._kwargs:
            sql = 'INSERT INTO {} ({}) VALUES ({})'
            return sql.format(self._table, ', '.join(self._kwargs),
                              ', '.join('%({})s'.format(f) for f in self._kwargs)), self._kwargs
        else:
            return ''

    def _update(self):
        sql = 'UPDATE {} SET {}'
        return sql.format(self._table,
                          ', '.join('{} = %({})s'.format(f, f) for f in self._kwargs)), self._kwargs

    def _delete(self):
        sql = 'DELETE FROM {}'
        return sql.format(self._table), {}

    def _where(self):
        if self._kwargs:
            args = {'cond_{}'.format(k): v for k, v in self._kwargs.items()}
            parser = ConditionParser()
            conditions = ['{}'.format(parser.parse(key, value)) for key, value in self._kwargs.items()]
            return ' WHERE {}'.format(
                ' AND '.join(conditions)), args
        else:
            return ''

    def _group_by(self):
        if len(self.fields) > 0:
            sql = ' GROUP BY {}'
            return sql.format(', '.join(self._args or self._kwargs)), {}

        return ''

    def _having(self):
        if self._kwargs:
            args = {'cond_{}'.format(k): v for k, v in self._kwargs.items()}
            parser = ConditionParser()
            conditions = ['{}'.format(parser.parse(key, value)) for key, value in self._kwargs.items()]
            return ' HAVING {}'.join(conditions), args
        else:
            return ''

    def _order_by(self):
        if len(self.fields) > 0:
            return 'ORDER BY {}'.format(', '.join(self._args or self._kwargs)), {}
        else:
            return ''


if __name__ == '__main__':
    l = ['a', 'b', 'c', 'd']
    d = {'a__lte': 100, 'b': 20, 'c': 30, 'd': 'hello', 'e': 'Wow'}
    s = SQLArgsFactory('test', 'where')
    print(s)
