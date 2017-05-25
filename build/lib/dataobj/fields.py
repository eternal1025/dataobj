# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : fields.py
# Date   : 2017-05-16 10-05
# Version: 0.0.1
# Description: description of this file.

import decimal
import datetime
import json
import pickle

from .exceptions import MissingColumnNameError, MissingFieldNameError
from .converters import PyDatetimeConverter
from .validators import (TypeValidator, NotNullValidator,
                         ChoiceValidator, LengthValidator)

__version__ = '0.0.1'
__author__ = 'Chris'


class BaseField(object):
    def __init__(self, db_column=None,
                 primary_key=False, default=None,
                 not_null=False, min_length=None,
                 max_length=None, auto_increment=True,
                 choices=None, validators=None):
        self._db_column = db_column
        self.field_name = ''
        self.primary_key = primary_key
        self._default = default
        self.not_null = not_null
        self.min_length = min_length
        self.max_length = max_length
        self.auto_increment = auto_increment
        self.choices = choices
        self._validators = list(validators or [])

        # Setup validators
        if self.primary_key is False and self.not_null is True:
            self._validators.append(NotNullValidator())
        elif self.primary_key is True and self.auto_increment is False:
            self._validators.append(NotNullValidator())

        if min_length or max_length:
            self._validators.append(LengthValidator(self.min_length, self.max_length))

        if choices:
            self._validators.append(ChoiceValidator(self.choices))

    def __repr__(self):
        return '<{} field_name={}, db_column={}>'.format(self.__class__.__name__,
                                                         self.field_name,
                                                         self.db_column)

    @property
    def db_column(self):
        return self._db_column or self.field_name

    @db_column.setter
    def db_column(self, value):
        self._db_column = value

    @property
    def default(self):
        return self._default() if (self._default and
                                   callable(self._default)) is True else self._default

    @default.setter
    def default(self, value):
        self._default = value

    @property
    def validators(self):
        return self._validators

    def validate_input(self, value):
        """
        Validate input value with multiple validators
        :param value: input value
        :return: valid value (maybe conversed after validation)
        """
        self.__ensure_valid_field_name_column_name()

        valid_value = value

        for validator in self.validators:
            valid_value = validator.validate(self.db_column, valid_value)

        return valid_value

    def validate_output(self, value):
        """
        Validate output value with multiple validators
        :param value: output value
        :return: valid value
        """
        self.__ensure_valid_field_name_column_name()

        valid_value = value

        for validator in self.validators:
            valid_value = validator.validate(self.field_name, valid_value)

        return valid_value

    def __ensure_valid_field_name_column_name(self):
        if not self.field_name:
            raise MissingFieldNameError('Field name is empty, set it first')

        if not self.db_column:
            raise MissingColumnNameError('Column name is empty,'
                                         'set field name and column name first')


class IntField(BaseField):
    """
    Map to MySQL int types:
    1. tinyint(m)       1 byte
    2. smallint(m)      2 bytes
    3. mediumint(m)     3 bytes
    4. int(m)           4 bytes
    5. bigint(m)        8 bytes
    """

    def __init__(self, db_column=None, primary_key=False,
                 default=None, not_null=False,
                 min_length=None, max_length=None,
                 auto_increment=True, choices=None,
                 validators=None):
        super().__init__(db_column, primary_key,
                         default, not_null,
                         min_length, max_length,
                         auto_increment, choices,
                         validators)
        self._validators.insert(0, TypeValidator(int))


class FloatField(BaseField):
    """
    Map to MySQL float types:
    1. float(m, d)      4 bytes， 8-bit precision
    2. double(m, d)     8 bytes, 16-bit precision
    """

    def __init__(self, db_column=None, primary_key=False,
                 default=None, not_null=False,
                 min_length=None, max_length=None,
                 auto_increment=True, choices=None,
                 validators=None):
        super().__init__(db_column, primary_key,
                         default, not_null,
                         min_length, max_length,
                         auto_increment, choices,
                         validators)
        self._validators.insert(0, TypeValidator(float))


class DecimalField(BaseField):
    """
    Map to MySQL decimal type:
    1. decimal(m, d)
    """

    def __init__(self, db_column=None, primary_key=False,
                 default=None, not_null=False,
                 min_length=None, max_length=None,
                 auto_increment=True, choices=None,
                 validators=None):
        super().__init__(db_column, primary_key,
                         default, not_null,
                         min_length, max_length,
                         auto_increment, choices,
                         validators)
        self._validators.insert(0, TypeValidator(decimal.Decimal))


class StrField(BaseField):
    """
    Map to MySQL string types:
    1. char(n)          fixed length, maximum 255 characters
    2. varchar(n)       fixed length, maximum 65535 characters
    3. tinytext         variable length, maximum 255 characters
    4. text             variable length, maximum 65535 characters
    5. mediumtext       variable length, maximum 2^24 -1 characters
    6. longtext         variable length, maximum 2^32 -1 characters
    """

    def __init__(self, db_column=None, primary_key=False,
                 default=None, not_null=False,
                 min_length=None, max_length=None,
                 auto_increment=True, choices=None,
                 validators=None):
        super().__init__(db_column, primary_key,
                         default, not_null,
                         min_length, max_length,
                         auto_increment, choices,
                         validators)
        self._validators.insert(0, TypeValidator(str))


class BlobField(BaseField):
    """
    Map to MySQL blob type:
    1. tinyblob
    2. mediumblob
    3. blob
    4. longblob
    """

    def __init__(self, db_column=None, primary_key=False,
                 default=None, not_null=False,
                 min_length=None, max_length=None,
                 auto_increment=True, choices=None,
                 validators=None):
        super().__init__(db_column, primary_key,
                         default, not_null,
                         min_length, max_length,
                         auto_increment, choices,
                         validators)
        self._validators.insert(0, TypeValidator(bytes))


class DateField(BaseField):
    """
    Map to MySQL date type
    """

    def __init__(self, db_column=None, primary_key=False,
                 default=None, not_null=False,
                 min_length=None, max_length=None,
                 auto_increment=True, choices=None,
                 validators=None):
        super().__init__(db_column, primary_key,
                         default, not_null,
                         min_length, max_length,
                         auto_increment, choices,
                         validators)
        self._validators.insert(0, TypeValidator(datetime.date,
                                                 force_converse_handler=lambda v:
                                                 PyDatetimeConverter().convert(v, 'date')))


class DatetimeField(BaseField):
    """
    Map to MySQL datetime type
    """

    def __init__(self, db_column=None, primary_key=False,
                 default=None, not_null=False,
                 min_length=None, max_length=None,
                 auto_increment=True, choices=None,
                 validators=None):
        super().__init__(db_column, primary_key,
                         default, not_null,
                         min_length, max_length,
                         auto_increment, choices,
                         validators)
        self._validators.insert(0, TypeValidator(datetime.datetime,
                                                 force_converse_handler=lambda v:
                                                 PyDatetimeConverter().convert(v, 'datetime')))


class TimeField(BaseField):
    """
    Map to MySQL time type
    """

    def __init__(self, db_column=None, primary_key=False,
                 default=None, not_null=False,
                 min_length=None, max_length=None,
                 auto_increment=True, choices=None,
                 validators=None):
        super().__init__(db_column, primary_key,
                         default, not_null,
                         min_length, max_length,
                         auto_increment, choices,
                         validators)
        self._validators.insert(0, TypeValidator(datetime.time,
                                                 force_converse_handler=lambda v:
                                                 PyDatetimeConverter().convert(v, 'time')))


class TimestampField(BaseField):
    """
    Map to MySQL timestamp type
    """

    def __init__(self, db_column=None, primary_key=False,
                 default=None, not_null=False,
                 min_length=None, max_length=None,
                 auto_increment=True, choices=None,
                 validators=None):
        super().__init__(db_column, primary_key,
                         default, not_null,
                         min_length, max_length,
                         auto_increment, choices,
                         validators)
        self._validators.insert(0, TypeValidator(datetime.datetime,
                                                 error_handler=lambda v: PyDatetimeConverter().convert(v, 'datetime')))


#
# Extended fields, for convenience
#

class BoolField(BaseField):
    """
    It means that this field can store a Python bool value
    """

    def __init__(self, db_column=None, primary_key=False,
                 default=None, not_null=False,
                 min_length=None, max_length=None,
                 auto_increment=True, choices=None,
                 validators=None):
        super().__init__(db_column, primary_key,
                         default, not_null,
                         min_length, max_length,
                         auto_increment, choices,
                         validators)
        self._validators.insert(0, TypeValidator(bool,
                                                 error_handler=lambda v: bool(v)))

    def validate_input(self, value):
        """
        Override it to translate `True` or `False` to 1 or 0

        Note: make sure this field in database if of `bit` or `int` type, not string type
        :param value:
        :return:
        """
        value = super().validate_input(value)
        try:
            return int(value)
        except TypeError:
            return 0


class _JsonSerializeDeserializeMixin(object):
    """
    Serialize or deserialize a value
    """

    def validate_input(self, value):
        return json.dumps(super().validate_input(value), ensure_ascii=False,
                          default=self._json_dumps_default)

    def validate_output(self, value):
        return super().validate_output(json.loads(value))


class ListField(_JsonSerializeDeserializeMixin, BaseField):
    """
    It means that this field can store a Python list

    Original value must be json SERIALIZABLE

    Note: Make sure the field in database is string type
    """

    def __init__(self, db_column=None, primary_key=False,
                 default=None, not_null=False,
                 min_length=None, max_length=None,
                 auto_increment=True, choices=None,
                 validators=None, json_dumps_default=None):
        super().__init__(db_column, primary_key,
                         default, not_null,
                         min_length, max_length,
                         auto_increment, choices,
                         validators)
        self._json_dumps_default = json_dumps_default
        self._validators.insert(0, TypeValidator(list))


class DictField(_JsonSerializeDeserializeMixin, BaseField):
    """
    It means that this field can store a Python dict

    Original value must be json SERIALIZABLE

    Note: Make sure the field in database is string type
    """

    def __init__(self, db_column=None, primary_key=False,
                 default=None, not_null=False,
                 min_length=None, max_length=None,
                 auto_increment=True, choices=None,
                 validators=None, json_dumps_default=None):
        super().__init__(db_column, primary_key,
                         default, not_null,
                         min_length, max_length,
                         auto_increment, choices,
                         validators)
        self._json_dumps_default = json_dumps_default
        self._validators.insert(0, TypeValidator(dict))


class _PickleSerializeDeserializeMixin(object):
    """
    Serialize and deserialize any Python object
    """

    def validate_input(self, value):
        return pickle.dumps(super().validate_input(value))

    def validate_output(self, value):
        return super().validate_output(pickle.loads(value))


class PickleField(_PickleSerializeDeserializeMixin, BaseField):
    """
    Almost any Python objects can be pickled
    This field can store a pickled object (just bytes actually)

    Note: Make sure the field in database is blob type
    """

    def __init__(self, db_column=None, primary_key=False,
                 default=None, not_null=False,
                 min_length=None, max_length=None,
                 auto_increment=True, choices=None,
                 validators=None):
        super().__init__(db_column, primary_key,
                         default, not_null,
                         min_length, max_length,
                         auto_increment, choices,
                         validators)


__all__ = ['BaseField', 'IntField', 'FloatField', 'DecimalField',
           'StrField', 'BlobField', 'DateField',
           'DatetimeField', 'TimeField', 'TimestampField',
           'ListField', 'DictField', 'PickleField', 'BoolField']
