# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : models.py
# Date   : 2017-05-16 10-05
# Version: 0.0.1
# Description: description of this file.

import logging
from pprint import pformat

from dataobj.exceptions import DuplicatePrimaryKeyError, PrimaryKeyNotFoundError
from dataobj.fields import *
from dataobj.manager import DataObjectsManager
from dataobj.utils import camel_to_underscore

logger = logging.getLogger(__name__)

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
        if attributes.get('__base_class__', False) is True:
            return type.__new__(mcs, name, bases, attributes)

        # Load dao class first
        try:
            dao_class = attributes.get('Meta').dao_class
        except AttributeError:
            raise RuntimeError('Missing dao_class attribute in Meta class, please define it first')

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
        attributes['__dao_class__'] = dao_class

        # Remove fields from attributes
        for key in mappings:
            attributes.pop(key)

        model = type.__new__(mcs, name, bases, attributes)
        setattr(model, 'objects', DataObjectsManager(model))
        return model

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
    Basic model
    """

    def __init__(self, **kwargs):
        for field_name, field_instance in self.__mappings__.items():
            field_value = kwargs.pop(field_name, None) or field_instance.default
            setattr(self, field_name, field_value)

    def __setattr__(self, key, value):
        field = self.__mappings__.get(key, None)
        if field is not None:
            self.__dict__[key] = field.validate_input(value)
        else:
            self.__dict__[key] = value

    def __getattribute__(self, item):
        field = object.__getattribute__(self, '__mappings__').get(item)
        if field is not None:
            return field.validate_output(self.__dict__.get(item))
        else:
            return object.__getattribute__(self, item)

    def __str__(self):
        return pformat(self.dict_data)

    @property
    def dict_data(self):
        return {k: v for k, v in self.__dict__.items() if k.startswith('_') is False}

    def dump(self):
        return self.objects.dump(self)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        return self.objects.update(self)

    def delete(self):
        return self.objects.delete(self)
