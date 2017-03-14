# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : object.py
# Date   : 2017-03-13 15-23
# Version: 0.0.1
# Description: description of this file.

import logging
from dataobj.field import Field
from sqlbuilder import SQLBuilder

from dataobj.exception import TableNotDefinedError, DuplicatePrimaryKeyError, PrimaryKeyNotFoundError

__version__ = '0.0.1'
__author__ = 'Chris'

logger = logging.getLogger(__name__)

DEBUG = False


class DataObjectMetaclass(type):
    """
    Metaclass scanner:
        it scans the DataObject fields, and collect them into special attributes.
    """

    def __new__(mcs, name, bases, attributes):
        # Ignore the original `DataObject`
        if name == 'DataObject':
            return type.__new__(mcs, name, bases, attributes)

        table = mcs._load_table(name, attributes)

        fields = []
        mappings = dict()
        primary_key = None

        for k, v in attributes.items():
            if not isinstance(v, Field):
                continue

            # Add field name first
            v.name = k
            logger.debug('Found mapping `{}`'.format(v))

            mappings[k] = v

            if v.primary_key is False:
                fields.append(v)
                continue

            if primary_key is None:
                logger.debug('Found primary key `{}`'.format(v))
                primary_key = v
            else:
                raise DuplicatePrimaryKeyError('Duplicate primary key `{}` found in `{}`'.format(k, name))

        if primary_key is None:
            raise PrimaryKeyNotFoundError('Missing primary key in `{}`'.format(name))

        attributes['__fields__'] = fields
        attributes['__mappings__'] = mappings
        attributes['__db_mappings__'] = {f.db_column: f for f in mappings.values()}
        attributes['__primary_key__'] = primary_key
        attributes['__table__'] = table

        # Remove fields from attributes
        for key in mappings:
            attributes.pop(key)

        return type.__new__(mcs, name, bases, attributes)

    @staticmethod
    def _load_table(name, attributes):
        # Find table name
        table = attributes.get('__table__', None)
        if table is None:
            raise TableNotDefinedError('{} missing attribute `__table__`, you must defined it first'.format(name))
        elif not isinstance(table, str):
            raise TypeError('`str` type expected for `__table__` attribute, not `{}`'.format(type(table)))
        elif table == '':
            raise TableNotDefinedError('Value of `__table__` attribute of {} is empty'.format(name))

        return table


class DataObject(metaclass=DataObjectMetaclass):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return '<{} {}>'.format(
            self.__class__.__name__,
            ', '.join(['{}={}'.format(key, getattr(self, key, None)) for key in self.__mappings__])
        )

    def save(self):
        """
        Save object to database

        :return: True/False
        """
        try:
            sql = SQLBuilder(self.__table__,
                             insert={f.db_column: self.__get_value_or_default(f.name) for f in self.__fields__}).sql
            setattr(self, self.__primary_key__.name, self._execute(sql))
            return True
        except Exception as err:
            logger.error(err, exc_info=DEBUG)
            return False

    @classmethod
    def load(cls, primary_key_value):
        """
        Load object from database

        :param primary_key_value: Value of the primary key
        :return:
        """
        try:
            sql = SQLBuilder(cls.__table__, select=[f.db_column for f in cls.__mappings__.values()],
                             where={cls.__primary_key__.db_column: primary_key_value}).sql
            result = cls._query(sql)

            data = None
            if isinstance(result, dict):
                data = result
            elif isinstance(result, list):
                data = result[0]

            return cls(**cls.__format_db_data(data))
        except Exception as err:
            logger.error(err, exc_info=DEBUG)
            return None

    def update(self, **kwargs):
        """
        Update object, save it to database

        :param kwargs: attr that you want to update
        :return: True/False
        """
        try:
            for k, v in kwargs.items():
                if k not in self.__mappings__:
                    continue

                setattr(self, k, v)

            cond = {self.__primary_key__.db_column: self.__get_value_or_default(self.__primary_key__.name)}
            sql = SQLBuilder(self.__table__,
                             update={f.db_column: self.__get_value_or_default(f.name) for f in self.__fields__},
                             where=cond).sql
            setattr(self, self.__primary_key__.name, self._execute(sql))
            return True
        except Exception as err:
            logger.error(err, exc_info=DEBUG)
            return False

    def delete(self):
        """
        Remove object from database

        :return:
        """
        try:
            cond = {self.__primary_key__.db_column: self.__get_value_or_default(self.__primary_key__.name)}
            sql = SQLBuilder(self.__table__,
                             delete='',
                             where=cond).sql
            self._execute(sql)
            return True
        except Exception as err:
            logger.error(err, exc_info=DEBUG)
            return False

    @classmethod
    def filter(cls, **where):
        try:
            sql = SQLBuilder(cls.__table__, select='*',
                             where=where).sql
            for row in cls._query(sql):
                try:
                    yield cls(**cls.__format_db_data(row))
                except Exception as err:
                    logger.error(err, exc_info=DEBUG)
                    continue

        except Exception as err:
            logger.error(err, exc_info=DEBUG)
            return None

    @classmethod
    def all(cls):
        try:
            sql = SQLBuilder(cls.__table__, select='*').sql

            for row in cls._query(sql):
                try:
                    yield cls(**cls.__format_db_data(row))
                except Exception as err:
                    logger.error(err, exc_info=DEBUG)
                    continue
        except Exception as err:
            logger.error(err, exc_info=DEBUG)
            return None

    @classmethod
    def __format_db_data(cls, data):
        d = dict()
        for k, v in data.items():
            f = cls.__db_mappings__.get(k)
            d[f.name] = f.output_format(v)

        return d

    def __get_value_or_default(self, key):
        field = self.__mappings__.get(key)
        value = getattr(self, field.name, None)
        if value:
            return field.db_format(value)
        else:
            return field.db_format(field.default_value)

    @staticmethod
    def _execute(sql):
        raise NotImplementedError

    @staticmethod
    def _query(sql):
        raise NotImplementedError


__all__ = ['DataObject']
