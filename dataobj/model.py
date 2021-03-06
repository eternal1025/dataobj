# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : models.py
# Date   : 2017-05-16 10-05
# Version: 0.0.1
# Description: description of this file.

import logging
from pprint import pformat

from .exceptions import DuplicatePrimaryKeyError, PrimaryKeyNotFoundError
from .fields import *
from .manager import DataObjectsManager
from .utils import camel_to_underscore

logger = logging.getLogger('dataobj')

__version__ = '0.0.1'
__author__ = 'Chris'


class ModelMeta(type):
    """
    Metaclass for a Database model.

    Add some new methods to an existing model.
    Check fields and so on.
    """

    def __new__(mcs, name, bases, attributes):
        # Ignore the original `DataObject`
        if name == 'Model':
            return type.__new__(mcs, name, bases, attributes)

        # Ignore `base model`
        try:
            if attributes.get('Meta').is_base_model is True:
                return type.__new__(mcs, name, bases, attributes)
        except:
            pass

        table_name = mcs.get_table_name(name, attributes)

        fields = []
        mappings = dict()
        primary_field = None

        for key, value in attributes.items():
            if isinstance(value, BaseField) is False:
                continue

            # Add field name first
            value.field_name = key
            logger.debug('Found mapping field `{}`'.format(value))

            mappings[key] = value

            if value.primary_key is False:
                fields.append(value)
                continue

            if primary_field is None:
                logger.debug('Found primary key field `{}`'.format(value))
                primary_field = value
            else:
                raise DuplicatePrimaryKeyError('Duplicate primary key `{}` found in `{}`'.format(key, name))

        if primary_field is None:
            raise PrimaryKeyNotFoundError('Missing primary key in `{}`'.format(name))

        attributes['__fields__'] = fields
        attributes['__mappings__'] = mappings
        attributes['__db_mappings__'] = {f.db_column: f for f in mappings.values()}
        attributes['__primary_field__'] = primary_field
        attributes['__table_name__'] = table_name
        # Connection could be a config with dict type or a server url,
        #  or a callable object that creates a database config,
        # or a object which implements the interfaces defined in `dbutil.connections.IDatabaseConnection`.
        try:
            attributes['__connection__'] = getattr(attributes.get('Meta'), 'connection')
        except AttributeError:
            attributes['__connection__'] = None

        # Remove fields from attributes
        for key in mappings:
            attributes.pop(key)

        model = type.__new__(mcs, name, bases, attributes)

        # INSTALL `DataObjectsManager` to handle db operations
        setattr(model, 'objects', DataObjectsManager(model))
        return model

    def __contains__(self, field_name):
        """
        Support `field_name` in `Model` syntax
        Easy way to check if the field_name exists in current model or not

        :return: True/False
        """
        return field_name in self.__mappings__

    @staticmethod
    def get_table_name(name, attributes):
        # Check it's Meta class, try to get the table name from
        meta = attributes.get('Meta', None)

        table_name = ''
        if meta is not None:
            table_name = getattr(meta, 'table_name', '')

        return table_name or camel_to_underscore(name)


class Model(metaclass=ModelMeta):
    """
    Basic model class

    Supported operations:
    1. Insert a new object to database: `model.dump()`
    2. Update an existing object: `model.update()`
    3. Delete an existing object: `model.delete()`
    4. Get an attribute: `model.attr_name` or `model['attr_name']`
    5. Set an attribute: `mode.attr_name = value` or `model['attr_name'] = value`
    6. Fields count: `len(model)`
    7. Check a field name is in the model or not: `field_name in model` or `field_name in Model`
    8. Get packed dict data: `model.dict_data`
    """

    def __init__(self, **kwargs):
        """
        Initialize fields of the model with given key-word arguments

        :param kwargs: dict
        """
        for field_name, field_instance in self.__mappings__.items():
            # field_value = kwargs.pop(field_name, None) or field_instance.default
            field_value = kwargs.pop(field_name, None)
            if field_value is None:
                field_value = field_instance.default

            setattr(self, field_name, field_value)

    def __setattr__(self, key, value):
        """
        Overwrite this method to validate the value of the key before
        assigning to a specific field

        :param key: any key (can be a field name of this model, or user-defined key)
        :param value: value of the key
        :return: None
        """
        field = self.__mappings__.get(key, None)
        if field is not None:
            self.__dict__[key] = field.validate_input(value)
        else:
            self.__dict__[key] = value

    def __getattribute__(self, item):
        """
        Validate the value of the given key `item` if `item` is a field name

        :param item: keyword
        :return: validated value
        """
        field = object.__getattribute__(self, '__mappings__').get(item)
        if field is not None:
            return field.validate_output(self.__dict__.get(item))
        else:
            return object.__getattribute__(self, item)

    def __repr__(self):
        return "<{class_name} data={data}>".format(class_name=self.__class__.__name__,
                                                   data=pformat(self.dict_data))

    def __contains__(self, field_name):
        """
        Support `field_name` in `model_instance` syntax
        Easy way to check if the field_name exists in current model or not

        :return: True/False
        """
        return field_name in self.__mappings__

    def __getitem__(self, item):
        """
        Emulating a dict: fetch a key's value

        Usage:
            value = model['field_name']
        """
        return getattr(self, item)

    def __setitem__(self, key, value):
        """
        Emulation a dict: set a key's value

        Usage:
            model['field_name'] = "FooBar"
        """
        return setattr(self, key, value)

    def __len__(self):
        """
        Count how many fields do we have
        """
        return len(self.__db_mappings__)

    @classmethod
    def from_raw_dict(cls, **kwargs):
        """
        Create a new model instance from original db row data
        """
        d = {}
        for column, value in kwargs.items():
            field = cls.__db_mappings__.get(column)
            if field is None:
                logger.info('Ignore column `{}` with value `{}`'.format(column, value))
                continue

            d[field.field_name] = value

        return cls(**d)

    @property
    def dict_data(self):
        return {k: getattr(self, k) for k in self.__mappings__}

    def dump(self, conn=None):
        """
        Insert it to the database
        """
        return self.objects.dump(self, conn)

    def update(self, conn=None, **kwargs):
        """
        Update a model instance and save it to the database
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

        return self.objects.update(self, conn)

    def delete(self, conn=None):
        """
        Delete a model instance
        """
        if self.objects.delete(self, conn) is True:
            # Clear all the existing values in the model instance
            self.__dict__.clear()
            return True
        return False
