# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : manager.py
# Date   : 2017-05-16 16-23
# Version: 0.0.2
# Description: description of this file.

import logging
import pickle

import copy
from dbutil import ConnectionRouter
from dbutil.sqlargs import SQLCondition

__version__ = '0.0.2'
__author__ = 'Chris'

logger = logging.getLogger('dataobj')


class DataObjectsManager(object):
    """
    DataObjectsManager: to handle database operations

    Functions:
    1. Insert a new model instance to database
    2. Update an existing model instance in database
    3. Delete an existing model instance from database
    4. Execute simple or complex queries, support lazy selection
    5. Support simple chained query call
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
        # Temporary inner cache to hold some query results for a while
        self._query_results_cache = None
        self._return_raw_data = False
        self._custom_conn = None

    def get(self, conn=None, **conditions):
        """
        Get a single item with the given conditions
        Shortcut of the query syntax: "model.objects.filter(conditions).first()"

        Return None if no one matched

        Usage:
        >>> result = model.objects.get(id=10)
        >>> print(result)
        """
        return self.filter(conn=conn, **conditions).first()

    def all(self, conn=None):
        """
        Get all the data objects (model instances)

        Usage:
        >>> results = model.objects.all()
        """
        return self.filter(conn)

    def filter(self, conn=None, **conditions):
        """
        Filter with the given conditions

        Usage:
        >>> results = model.objects.filter(field_name__startswith="foobar")
        >>> results.first()
        >>> results.last()
        >>> results[:10]
        >>> results[4]
        """
        self._custom_conn = conn
        o = copy.deepcopy(self)
        o._query_collector['select'] = list(self._model.__mappings__.keys())
        o._query_collector['where'] = conditions
        o._return_raw_data = False
        return o

    def filter_with_field_names(self, conn=None, *field_names, **conditions):
        """
        Filter specific fields with the given conditions

        Return the original dict data fetched from database
        """
        self._custom_conn = conn
        o = copy.deepcopy(self)
        o._query_collector['select'] = field_names
        o._query_collector['where'] = conditions
        o._return_raw_data = True
        return o

    def limit(self, how_many, offset=0):
        """
        Limit rows

        Usage:
        >>> for x in model.objects.all().limit(10):
        >>>     print(x)

        >>> for x in model.objects.all().limit(10, 10):
        >>>     print(x)
        """
        o = copy.deepcopy(self)
        o._query_collector['limit'] = (how_many, offset)
        return o

    def order_by(self, *field_names, descending=False):
        """
        Order by field names

        Set descending order to True to get reversed rows

        Usage:
        >>> for x in model.objects.all().order_by(some_field).limit(10):
        >>>     print(x)
        """
        o = copy.deepcopy(self)
        o._query_collector['order_by'] = field_names
        o._query_collector['descending'] = descending
        return o

    def first(self):
        """
        To get the first item from results

        Usage:
        >>> obj = model.objects.all().first()
        """
        self._fetch_results()
        if len(self._query_results_cache) > 0:
            return self._query_results_cache[0]

        return None

    def last(self):
        """
        To get the last item from results

        Usage:
        >>> obj = model.objects.all().last()
        """
        self._fetch_results()
        if len(self._query_results_cache) > 0:
            return self._query_results_cache[-1]

        return None

    @staticmethod
    def _get_pk_name(model_instance):
        """For pickling attribute"""
        return '{}_pk'.format(model_instance.__class__.__name__)

    def dump(self, model_instance, conn=None):
        """
        Insert the model instance to database immediately
        """
        primary_field = model_instance.__primary_field__

        # Do not insert primary value when `auto_increment` is enabled
        fields = model_instance.__fields__ if primary_field.auto_increment is True \
            else model_instance.__mappings__.values()

        content = {field.db_column: model_instance.__dict__.get(field.field_name) for field in fields}
        result = self._execute(self._model.__table_name__, conn, insert=content)
        if result:
            last_id = result[-1]
            if primary_field.auto_increment is True:
                setattr(model_instance, primary_field.field_name, last_id)
                setattr(model_instance, self._get_pk_name(model_instance), pickle.dumps(model_instance))
            return True
        else:
            logger.error('Error happened during dumping')
            return False

    def _collect_updated_content(self, model_instance):
        """Only fields that were updated with new values will be updated into database"""
        pk = getattr(model_instance, self._get_pk_name(model_instance), None)
        if pk is None:
            return {field.db_column: model_instance.__dict__[field.field_name] for field in
                    model_instance.__fields__}
        else:
            old_instance = pickle.loads(pk)
            content = {}

            for field in model_instance.__fields__:
                if old_instance.__dict__[field.field_name] == model_instance.__dict__[field.field_name]:
                    continue
                content[field.db_column] = model_instance.__dict__[field.field_name]

            return content

    def update(self, model_instance, conn=None):
        """
        Update the model instance in database
        """
        primary_field = model_instance.__primary_field__
        value_of_primary_key = model_instance.__dict__.get(primary_field.field_name)
        content = self._collect_updated_content(model_instance)

        if len(content) == 0:
            return True

        logger.debug('Update model "{}" with content "{}"'.format(model_instance.__class__.__name__, content))
        where = {primary_field.db_column: value_of_primary_key}
        result = self._execute(self._model.__table_name__,
                               conn,
                               update=content, where=where)
        if result is None:
            return False
        else:
            setattr(model_instance, self._get_pk_name(model_instance), pickle.dumps(model_instance))

        return True

    def delete(self, model_instance, conn=None):
        """
        Delete the model instance from database
        """
        primary_field = model_instance.__primary_field__
        value_of_primary_key = model_instance.__dict__.get(primary_field.field_name)

        result = self._execute(self._model.__table_name__,
                               conn,
                               delete='',
                               where={primary_field.db_column: value_of_primary_key})
        return True if result is not None else False

    def count(self, conn=None):
        """
        Count how many rows in a table

        # TO-DO: extend sqlargs package to support MYSQL FUNCTIONS
        """
        try:
            return list(self._query(self._model.__table_name__, conn, select=['COUNT(1) AS cnt']))[0].get('cnt')
        except Exception as err:
            logger.error(err)
            return -1

    def _fetch_results(self):
        """
        Check the temporary cache before selecting rows from database
        """
        if self._query_results_cache is None:
            if self._return_raw_data is True:
                self._query_results_cache = list(self._select_now(self._custom_conn))
            else:
                self._query_results_cache = list(self._iter_objects(self._custom_conn))

    def _iter_objects(self, conn=None):
        """
        Generate model objects from query results
        """
        for row in self._select_now(conn):
            o = self._model(**row)
            setattr(o, self._get_pk_name(o), pickle.dumps(o))
            yield o

    def _select_now(self, conn=None):
        """
        Now execute the collected queries and return the query results
        """
        # fields to select
        field_names = self._query_collector['select'] or []
        selected_columns = []

        for field_name in field_names:
            if field_name not in self._model:
                raise ValueError('Field `{}` is not defined in class `{}`'.format(field_name, self._model.__name__))

            selected_columns.append(self._model.__mappings__.get(field_name).db_column)

        # translate conditions
        where = {}
        for k, v in (self._query_collector['where'] or {}).items():
            sql_cond = SQLCondition(k, v)
            field_name = sql_cond.field_name
            if field_name not in self._model:
                raise ValueError('Field `{}` is not defined in class `{}`'.format(field_name, self._model.__name__))

            field = self._model.__mappings__.get(field_name)
            # where['{}__{}'.format(field.db_column, sql_cond.condition)] = field.validate_input(v)
            where['{}__{}'.format(field.db_column, sql_cond.condition)] = v

        order_by_columns = list()

        for field_name in self._query_collector['order_by'] or []:
            if field_name not in self._model:
                raise ValueError('Field `{}` is not defined in model `{}`'.format(field_name, self._model.__name__))

            order_by_columns.append(self._model.__mappings__.get(field_name).db_column)

        # build sql args
        kwargs = {"select": selected_columns,
                  "where": where,
                  "limit": self._query_collector['limit']}

        if self._query_collector['descending'] is True:
            kwargs['descending_order_by'] = order_by_columns
        else:
            kwargs['ascending_order_by'] = order_by_columns

        # Translate column to real field names
        for row in self._query(self._model.__table_name__, conn, **kwargs):
            converted_row = {}
            for column, value in row.items():
                model_field = self._model.__db_mappings__.get(column)

                if model_field:
                    converted_row[model_field.field_name] = model_field.validate_output(value)

            yield converted_row

        self._custom_conn = None

    def _execute(self, table, conn=None, **kwargs):
        conn = self._get_connection(conn)
        try:
            conn.open()
        except AttributeError:
            pass

        try:
            return conn.execute(table, **kwargs)
        except Exception as err:
            raise err
        finally:
            try:
                conn.close()
            except AttributeError:
                pass

    def _query(self, table, conn=None, **kwargs):
        conn = self._get_connection(conn)
        try:
            conn.open()
        except AttributeError:
            pass

        try:
            return conn.query(table, **kwargs)
        except Exception as err:
            raise err
        finally:
            try:
                conn.close()
            except AttributeError:
                pass

    def _get_connection(self, conn):
        conn = conn or self._model.__connection__

        if callable(conn):
            conn = conn()

        if isinstance(conn, (dict, str)):
            return ConnectionRouter(conn)
        else:
            if hasattr(conn, 'execute') and hasattr(conn, 'query'):
                return conn
            raise RuntimeError("Connection is not properly configured")

    #############################
    # Python's special methods  #
    #############################

    def __repr__(self):
        return "<DataObjectsManager model={}>".format(self._model.__name__)

    def __getitem__(self, item):
        """
        To support slicing and iteration

        :param item: slice index
        :return: one or more items
        """
        self._fetch_results()
        return self._query_results_cache[item]

    def __len__(self):
        """
        Support len(...) function to get the length of data objects
        :return: length of data objects
        """
        self._fetch_results()
        return len(self._query_results_cache)

    def __deepcopy__(self, memo):
        """Do not copy the temporary cache results to the new manager instance"""

        o = self.__class__(self._model)
        for k, v in self.__dict__.items():
            if k == '_query_results_cache':
                o.__dict__[k] = None
            else:
                o.__dict__[k] = copy.deepcopy(v, memo)

        return o
