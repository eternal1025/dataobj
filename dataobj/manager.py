# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : manager.py
# Date   : 2017-05-16 16-23
# Version: 0.0.1
# Description: description of this file.

import logging
from dataobj.sqlargs import SQLArgsBuilder, SQLCondition

__version__ = '0.0.1'
__author__ = 'Chris'

logger = logging.getLogger(__name__)


class DataObjectsManager(object):
    """
    Lazy selection
    """

    def __init__(self, model):
        self._model = model
        self._query_collector = {
            'select': None,
            'where': None,
            'limit': None,
            'order_by': None,
            'descending': False
        }

    def __iter__(self):
        yield from self._select_now()

    def get(self, **conditions):
        """
        Get a single item with given condition
        """
        return self.filter(**conditions).first()

    def all(self):
        return self.filter()

    def filter(self, **conditions):
        return self.filter_with_field_names(*self._model.__mappings__.values(), **conditions)

    def filter_with_field_names(self, *field_names, **conditions):
        self._query_collector['select'] = field_names
        self._query_collector['where'] = conditions
        return self

    def limit(self, n):
        self._query_collector['limit'] = n
        return self

    def order_by(self, *field_names, descending=False):
        self._query_collector['order_by'] = field_names
        self._query_collector['descending'] = descending
        return self

    def first(self):
        results = list(self)[:1]
        if len(results) > 0:
            return results[0]

        return None

    def last(self):
        results = list(self)[-1:]
        if len(results) > 0:
            return results[0]

        return None

    def dump(self, model_instance):
        primary_field = model_instance.__primary_field__

        # Do not insert primary value when `auto_increment` is enabled
        fields = model_instance.__fields__ if primary_field.auto_increment is True \
            else model_instance.__mappings__.values()

        content = {field.db_column: getattr(model_instance, field.field_name) for field in fields}
        last_id = self._execute(*SQLArgsBuilder(self._model.__table_name__,
                                                insert=content).sql_args)

        if primary_field.auto_increment is True:
            setattr(model_instance, primary_field.field_name, last_id)

        return True

    def update(self, model_instance):
        primary_field = model_instance.__primary_field__
        value_of_primary_key = getattr(model_instance, primary_field.field_name)
        content = {field.db_column: getattr(model_instance, field.field_name) for field in model_instance.__fields__}
        where = {primary_field.db_column: value_of_primary_key}

        self._execute(*SQLArgsBuilder(self._model.__table_name__,
                                      update=content,
                                      where=where).sql_args)

        return True

    def delete(self, model_instance):
        primary_field = model_instance.__primary_field__
        value_of_primary_key = getattr(model_instance, primary_field.field_name)

        self._execute(*SQLArgsBuilder(self._model.__table_name__,
                                      delete='',
                                      where={primary_field.db_column: value_of_primary_key}).sql_args)

        return True

    def _select_now(self):
        # fields to select
        fields = self._query_collector['select'] or []
        selected_columns = [field.db_column for field in fields]

        # translate conditions
        where = {}
        for k, v in (self._query_collector['where'] or {}).items():
            sql_cond = SQLCondition(k, v)
            field_name = sql_cond.field_name
            if field_name not in self._model.__mappings__:
                raise ValueError('Field `{}` is not defined in class `{}`'.format(field_name, self._model.__name__))

            field = self._model.__mappings__.get(field_name)
            where['{}__{}'.format(field.db_column, sql_cond.condition)] = v

        order_by_columns = list()

        for field_name in self._query_collector['order_by'] or []:
            if field_name not in self._model.__mappings__:
                raise ValueError('Field `{}` is not defined in class `{}`'.format(field_name, self._model.__name__))

            field = self._model.__mappings__.get(field_name)
            order_by_columns.append(field.db_column)

        # build sql args
        kwargs = {"select": selected_columns,
                  "where": where,
                  "limit": self._query_collector['limit']}

        if self._query_collector['descending'] is True:
            kwargs['descending_order_by'] = order_by_columns
        else:
            kwargs['ascending_order_by'] = order_by_columns

        sql, args = SQLArgsBuilder(self._model.__table_name__,
                                   **kwargs).sql_args

        for row in self._query(sql, args):
            converted_row = {}
            for column, value in row.items():
                model_field = self._model.__db_mappings__.get(column)

                if model_field:
                    converted_row[model_field.field_name] = model_field.validate_output(value)
                else:
                    logger.info('Ignore column `{}` with value `{}`'.format(column, value))

            yield self._model(**converted_row)

    def _execute(self, sql, args):
        # print('Execute sql "{}" with args "{}"'.format(sql, args))
        logger.debug('Execute sql "{}" with args "{}"'.format(sql, args))

        # Return the last row id
        return self._model.__dao_class__.execute(sql, args)

    def _query(self, sql, args):
        # print('Query sql "{}" with args "{}"'.format(sql, args))
        logger.debug('Query sql "{}" with args "{}"'.format(sql, args))
        return self._model.__dao_class__.query(sql, args)
