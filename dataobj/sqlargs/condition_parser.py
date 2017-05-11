# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : condition_parser.py
# Date   : 2017-05-11 15-56
# Version: 0.0.1
# Description: description of this file.


__version__ = '0.0.1'
__author__ = 'Chris'


class ConditionParser(object):
    """
    Usage cond__eq = 3
    """
    condition_maps = {
        'eq': lambda _: '{field} = %(cond_{key})s',
        'lt': lambda _: '{field} < %(cond_{key})s',
        'gt': lambda _: '{field} > %(cond_{key})s',
        'lte': lambda _: '{field} <= %(cond_{key})s',
        'gte': lambda _: '{field} >= %(cond_{key})s',
        'ne': lambda _: '{field} != %(cond_{key})s',
        'contains': lambda _: '{field} LIKE "%%%(cond_{key})s%%"',
        'startswith': lambda _: '{field} LIKE "%%(cond_{key}s)"',
        'endswith': lambda _: '{field} LIKE "%(cond_{key})s%%"',
        'isnull': lambda flag: '{field} IS NULL' if flag is True else '{field} IS NOT NULL'
    }

    def parse(self, key, value=None):
        assert isinstance(key, str)

        *field_parts, condition_mark = key.split('__')

        if len(field_parts) == 0:
            field = key
            condition_mark = 'eq'
        else:
            field = ''.join(field_parts)

        get_expression = self.condition_maps.get(condition_mark, None)
        if get_expression:
            return get_expression(value).format(field=field, key=key)

        raise ValueError('Unsupported condition mark `{}` for field `{}`'.format(condition_mark, field))


if __name__ == '__main__':
    parser = ConditionParser()
    exp = parser.parse('a__endswith')
    print(exp)
    print(exp % {'a': 'hello, world'})
