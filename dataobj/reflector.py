# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : reflector.py
# Date   : 2017-05-19 09-05
# Version: 0.0.1
# Description: Generate a model from the given table automatically

from .utils import validate_dao_class, underscore_to_camel
from .fields import *

__version__ = '0.0.1'
__author__ = 'Chris'


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

    def reflect(self, table, model_name='', **field_name_mappings):
        """
        Generate a Model class from the given table

        :param table: table name
        :param model_name: custom model name (default model name is table.capitalize())
        :param field_name_mappings: custom field mappings, key is your custom field name,
                            value is the column in database
        :return: formatted Model class str
        """
        return self._create_model(table, model_name,
                                  *self._translate_descriptions_to_fields(*self._describe_table(table),
                                                                          **field_name_mappings))

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

    def _translate_descriptions_to_fields(self, *descriptions, **field_name_mappings):
        fields = []
        reversed_mappings = dict((v, k) for k, v in field_name_mappings.items())

        for column in descriptions:
            column_name = column.get('Field')
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
                field_name=reversed_mappings.get(column_name) or column_name,
                field_class=field_class.__name__,
                kwargs=kwargs)
            fields.append(field)

        return fields

    @staticmethod
    def _create_model(table, model_name='', *fields):
        assert isinstance(model_name, str)
        model_name = underscore_to_camel(table) if not model_name else model_name

        model_templates = ["class {model_name}(Model):".format(model_name=model_name)]

        for field in fields:
            model_templates.append("    {field}".format(field=field))

        # Add meta class
        model_templates.append('')
        model_templates.append("    class Meta:\n"
                               "        table_name = '{}'\n"
                               "        dao_class = DaoClass".format(table))
        model_templates.append('')

        return '\n'.join(model_templates)
