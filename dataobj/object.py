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

from pprint import pformat
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

        # Ignore `base data object`
        if attributes.get('__base_class__', False) is True:
            return type.__new__(mcs, name, bases, attributes)

        if not attributes.get('__dao_class__', None):
            raise RuntimeError('Dao class is not defined yet')

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
            raise TableNotDefinedError('{} missing attribute `__table__`, you must define it first'.format(name))
        elif not isinstance(table, str):
            raise TypeError('`str` type expected for `__table__` attribute, not `{}`'.format(type(table)))
        elif table == '':
            raise TableNotDefinedError('Value of `__table__` attribute of {} is empty'.format(name))

        return table


class DataObject(metaclass=DataObjectMetaclass):
    __table__ = None
    __dao_class__ = None

    def __init__(self, **kwargs):
        fields = list(self.__mappings__.keys())

        # Set attribute from arguments
        for k, v in kwargs.items():
            setattr(self, k, v)
            if k in fields:
                fields.remove(k)
            else:
                logger.debug('Unknown field {}'.format(k))

        # Otherwise, set attribute with default value
        for f in fields:
            setattr(self, f, self.__get_value_or_default(f, False))

    def __repr__(self):
        return '<{} {}>'.format(
            self.__class__.__name__,
            ', '.join(['{}={}'.format(key, getattr(self, key, None)) for key in self.__mappings__])
        )

    def __str__(self):
        return pformat(', '.join(['{}={}'.format(key, getattr(self, key, None)) for key in self.__mappings__]))

    @property
    def dict_data(self):
        return {k: getattr(self, k, None) for k in self.__mappings__}

    @classmethod
    def has_field(cls, field_name):
        return field_name in cls.__mappings__

    def dump(self):
        """
        Insert object to the database

        :return: True/False
        """
        try:
            primary_key_value = getattr(self, self.__primary_key__.name, None)

            d = self.__as_db_dict()

            if primary_key_value is not None:
                d[self.__primary_key__.db_column] = primary_key_value

            sql = SQLBuilder(self.__table__,
                             insert=d).sql

            if primary_key_value is not None:
                self._execute(sql)
            else:
                setattr(self, self.__primary_key__.name, self._execute(sql))

            return True
        except Exception as err:
            logger.error(err, exc_info=DEBUG)
            return False

    @classmethod
    def from_raw_dict(cls, **kwargs):
        """
        Create a new DataObject instance from given the dict

        :param kwargs:
        :return:
        """
        try:
            return cls(**cls.__format_db_data(kwargs))
        except Exception as err:
            logger.error(err, exc_info=DEBUG)

    @classmethod
    def load(cls, primary_key_value):
        """
        Load object from the database

        :param primary_key_value: Value of the primary key
        :return:
        """
        try:
            return cls.filter(**{cls.__primary_key__.name: primary_key_value})[0]
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
            field_names = [f.name for f in self.__fields__]

            for k, v in kwargs.items():
                if k not in field_names:
                    continue

                setattr(self, k, v)

            cond = {self.__primary_key__.db_column: self.__get_value_or_default(self.__primary_key__.name)}
            sql = SQLBuilder(self.__table__,
                             update=self.__as_db_dict(),
                             where=cond).sql
            self._execute(sql)
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
        result = cls.filter_iter(**where)
        return list(result) if result is not None else []

    @classmethod
    def filter_with_fields(cls, *fields, **where):
        result = cls.filter_with_fields_iter(*fields, **where)
        return list(result) if result is not None else []

    @classmethod
    def filter_with_fields_iter(cls, *fields, **where):
        try:
            assert len(fields) > 0, ValueError('Fields are not specified yet')
            db_fields = [cls.__mappings__.get(x).db_column for x in fields if x in cls.__mappings__]
            for row in cls._query(SQLBuilder(cls.__table__, select=db_fields,
                                             where=cls.__safe_conditions(**where)).sql):
                yield cls.__format_db_data(row)
        except Exception as err:
            logger.error(err, exc_info=DEBUG)

    @classmethod
    def filter_iter(cls, **where):
        try:
            for row in cls.filter_with_fields_iter(*[f.name for f in cls.__fields__],
                                                   **where):
                yield cls(**row)
        except Exception as err:
            logger.error(err, exc_info=DEBUG)
            return None

    @classmethod
    def all(cls):
        return cls.filter()

    @classmethod
    def all_iter(cls):
        yield from cls.filter_iter()

    @classmethod
    def count(cls, field=None):
        sql = 'SELECT COUNT({field}) AS count FROM {table}'.format(
            field=1 if field not in cls.__fields__ else field,
            table=cls.__table__
        )
        try:
            return cls._query(sql)[0]['count']
        except Exception as err:
            logger.error(err, exc_info=DEBUG)

    @classmethod
    def __safe_conditions(cls, **where):
        # replace query condition keys with the real ones
        conditions = {}
        for k, v in where.items():
            f = cls.__mappings__.get(k)
            if f is None:
                raise AttributeError('Field `{}` is not defined in class `{}`'.format(k, cls.__name__))

            conditions[f.db_column] = v

        return conditions

    def __as_db_dict(self):
        return {f.db_column: self.__get_value_or_default(f.name) for f in self.__fields__}

    @classmethod
    def __format_db_data(cls, data):
        d = dict()
        for k, v in data.items():
            f = cls.__db_mappings__.get(k)

            if f is None:
                logger.debug('Missing field `{}` with value `{}`'.format(k, v))
                continue

            d[f.name] = f.output_format(v)

        return d

    def __get_value_or_default(self, key, format_=True):
        field = self.__mappings__.get(key)
        value = getattr(self, field.name, None)

        if value is None:
            value = field.default_value
            setattr(self, key, value)

        return field.db_format(value) if format_ else value

    @classmethod
    def _query(cls, sql):
        logger.debug('Query SQL: {}'.format(sql))
        return cls.__dao_class__().query(sql)

    def _execute(self, sql):
        logger.debug('Execute SQL: {}'.format(sql))
        return self.__dao_class__().execute(sql)


__all__ = ['DataObject']
