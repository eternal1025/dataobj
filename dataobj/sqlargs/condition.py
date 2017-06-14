# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : condition_parser.py
# Date   : 2017-05-11 15-56
# Version: 0.0.1
# Description: description of this file.

__version__ = '0.0.1'
__author__ = 'Chris'


class SQLCondition(object):
    """
    Represent a condition object.

    Currently supported conditions:
    1. eq: = (default condition)
    2. lt: <
    3. lte: <=
    4. gt: >
    5. gte: >=
    6. ne: !=
    7. contains
    8. startswith
    9. endswith,
    10. isnull
    """
    CONDITION_MAPS = {
        'eq': lambda _: '{field} = %(cond_{key}_{salt})s',
        'lt': lambda _: '{field} < %(cond_{key}_{salt})s',
        'gt': lambda _: '{field} > %(cond_{key}_{salt})s',
        'lte': lambda _: '{field} <= %(cond_{key}_{salt})s',
        'gte': lambda _: '{field} >= %(cond_{key}_{salt})s',
        'ne': lambda _: '{field} != %(cond_{key}_{salt})s',
        'in': lambda kinds: '{field} IN ' +
                            '({})'.format(', '.join('%(cond_{key}_' + str(v) + '_{salt})s' for v in list(kinds))),
        'range': lambda _: '{field} BETWEEN %(cond_{key}_from_{salt})s AND %(cond_{key}_to_{salt})s',
        'contains': lambda _: '{field} LIKE CONCAT("%%", %(cond_{key}_{salt})s, "%%")',
        'startswith': lambda _: '{field} LIKE CONCAT(%(cond_{key}_{salt})s, "%%")',
        'endswith': lambda _: '{field} LIKE CONCAT("%%", %(cond_{key}_{salt})s)',
        'isnull': lambda flag: '{field} IS NULL' if flag is True else '{field} IS NOT NULL'
    }

    # SELECT create_at, icon_url, id, name FROM folder WHERE name LIKE '%文件夹%'

    def __init__(self, key, value=None, salt=None):
        """
        :param key: condition key
        :param value: value of the condition
        :param salt: add salt to avoid duplicate field
        """
        self._key = key
        self._value = value
        self._field = ''
        self._condition = ''
        self._salt = salt or 'xYzd'
        self.__parse_condition()

    def __repr__(self):
        return '<Condition field="{}", condition="{}", sql="{}">'.format(self.field_name, self.condition, self.sql)

    @property
    def field_name(self):
        """
        Real field name of that condition
        :return: str
        """
        return self._field

    @property
    def sql(self):
        get_expression = self.CONDITION_MAPS.get(self._condition, None)
        return get_expression(self._value).format(field=self._field, key=self._key, salt=self._salt or '')

    @property
    def args(self):
        if self.condition == 'range':
            return {'cond_{}_from_{}'.format(self._key, self._salt): self._value[0],
                    'cond_{}_to_{}'.format(self._key, self._salt): self._value[1]}
        if self.condition == 'in':
            return {'cond_{}_{}_{}'.format(self._key, v, self._salt): str(v) for v in self._value}

        return {'cond_{}_{}'.format(self._key, self._salt): self._value}

    @property
    def condition(self):
        return self._condition

    def __parse_condition(self):
        assert isinstance(self._key, str)

        *field_parts, condition_mark = self._key.split('__')

        if len(field_parts) == 0:
            self._field = self._key
            condition_mark = 'eq'
        else:
            self._field = ''.join(field_parts)

        if condition_mark in self.CONDITION_MAPS:
            self._condition = condition_mark
        else:
            raise ValueError('Unsupported condition mark `{}` for field `{}`'.format(condition_mark, self._field))


__all__ = ['SQLCondition']

if __name__ == '__main__':
    # parser = ConditionParser()
    # exp = parser.parse('a__endswith')
    # print(exp)
    # print(exp % {'a': 'hello, world'})
    condition = SQLCondition('a__in', {1, 3, 4})
    print(condition)
    print(condition.args)
