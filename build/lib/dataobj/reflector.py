# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : reflector.py
# Date   : 2017-05-19 09-05
# Version: 0.0.1
# Description: Generate a model from the given table automatically

import logging
import dataobj
from .utils import validate_dao_class, underscore_to_camel
from .fields import *

__version__ = '0.0.1'
__author__ = 'Chris'

__all__ = ['ReflectedModel', 'MySQLTableReflector']

logger = logging.getLogger(__name__)


class ReflectedModel(object):
    def __init__(self, name, field_classes, template):
        self.name = name
        self.field_classes = field_classes
        self.template = template

    def __str__(self):
        return self.template


class MySQLTableReflector(object):
    """
    Just a handy tool for MySQL to generate a Model class automatically

    Columns in database will be mapped to corresponding field types list in `dataobj.fields`
    """

    # Type mappings (only a subset of the full supported types in MySQL)
    # Numeric types
    tinyint = IntField
    smallint = IntField
    mediumint = IntField
    int = IntField
    bigint = IntField

    float = FloatField
    double = FloatField

    decimal = FloatField

    # Character types
    char = StrField
    varchar = StrField
    tinytext = StrField
    text = StrField
    mediumtext = StrField
    longtext = StrField

    # Blob types
    tinyblob = BlobField
    mediumblob = BlobField
    blob = BlobField
    longblob = BlobField

    # Date time types
    date = DateField
    datetime = DatetimeField
    time = TimeField
    timestamp = TimestampField

    def __init__(self, dao_class):
        """
        Initialize this reflector
        :param dao_class: A dao class which implements two methods `execute(sql, args)` and
                        `query(sql, args)`
        """
        # Validate dao class first
        validate_dao_class(dao_class)
        self._dao_class = dao_class
        self._type_mappings = {}

    def __repr__(self):
        return '<"{}" object with dao class "{}">'.format(self.__class__.__name__,
                                                          self._dao_class)

    @property
    def tables_can_be_reflected(self):
        """
        Return tables can be reflected in the activated database
        """
        try:
            tables = []
            for item in self._dao_class().query("SHOW TABLES;", None):
                tables.append(list(item.values())[0])
            return tables
        except Exception as err:
            logger.error(err)
            return []

    def reflect(self, table, model_name='', skip_columns=None, keep_columns=None,
                field_name_mappings=None,
                field_type_mappings=None):
        """
        Generate a Model class from the given table

        :param table: table name
        :param model_name: custom model name
        :param skip_columns: column names to be skipped
        :param keep_columns: column names to be used (if skip_columns is defined, it will be ignored)
        :param field_type_mappings: custom field type mappings
        :param field_name_mappings: custom field mappings, key is your custom field name,
                            value is the column in database
        :return: formatted Model class str
        """
        return self._create_model(table, model_name,
                                  *self._translate_descriptions_to_fields(self._describe_table(table),
                                                                          skip_columns or [],
                                                                          keep_columns or [],
                                                                          field_name_mappings or {},
                                                                          field_type_mappings or {}))

    @classmethod
    def get_type_mappings(cls):
        if hasattr(cls, '_type_mappings'):
            return getattr(cls, '_type_mappings')

        mappings = {}
        for attr, value in cls.__dict__.items():
            if attr.startswith('_'):
                continue

            try:
                if value.__name__.endswith('Field'):
                    mappings[attr] = value
            except:
                pass

        setattr(cls, '_type_mappings', mappings)
        return mappings

    def _describe_table(self, table):
        return self._dao_class().query('DESC {}'.format(table), None)

    def _translate_descriptions_to_fields(self, descriptions, skip_columns, keep_columns, field_name_mappings,
                                          field_type_mappings):
        fields = []
        field_classes = []
        reversed_mappings = dict((v, k) for k, v in field_name_mappings.items())

        for column in descriptions:
            column_name = column.get('Field')
            if column_name in skip_columns:
                continue

            if keep_columns and column_name not in keep_columns:
                continue

            type_with_size = column.get('Type')
            column_type, *size = type_with_size.split('(')
            try:
                column_size = int(''.join(size).strip(')'))
            except:
                column_size = None

            column_default = column.get('Default')
            is_primary_key = column.get('Key') == 'PRI'
            auto_increment = column.get('Extra') == 'auto_increment'
            not_null = column.get('Null') != 'YES'

            # Create our field
            field_name = reversed_mappings.get(column_name) or column_name

            if field_name in field_type_mappings:
                field_class = getattr(dataobj, field_type_mappings.get(field_name))
            else:
                field_class = self.get_type_mappings().get(column_type)

            kwargs = {
                'db_column': "'{}'".format(column_name) if column_name in reversed_mappings else '',
                'primary_key': is_primary_key,
                'auto_increment': auto_increment,
                'not_null': not_null,
                'default': column_default,
                'max_length': column_size
            }

            kwargs = ', '.join('{}={}'.format(k, kwargs[k]) for k in sorted(kwargs) if kwargs[k])
            field = '{field_name} = {field_class}({kwargs})'.format(
                field_name=field_name,
                field_class=field_class.__name__,
                kwargs=kwargs)
            fields.append(field)
            field_classes.append(field_class)

        return fields, field_classes

    def _create_model(self, table, model_name, fields, field_classes):
        assert isinstance(model_name, str)
        model_name = underscore_to_camel(table) if not model_name else model_name
        model_templates = ["class {model_name}(Model):".format(model_name=model_name)]

        for field in sorted(fields):
            if 'primary_key=True' in field:
                model_templates.insert(1, '    {field}'.format(field=field))
            else:
                model_templates.append("    {field}".format(field=field))

        # Add meta class
        model_templates.append('')
        model_templates.append("    class Meta:\n"
                               "        table_name = '{}'\n"
                               "        dao_class = {}".format(table, self._dao_class.__name__))
        model_templates.append('')

        return ReflectedModel(model_name, field_classes, '\n'.join(model_templates))
