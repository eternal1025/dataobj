# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: MIT License
# File   : test_validators.py
# Date   : 2017-07-26 14-52
# Version: 0.1
# Description: description of this file.

import pytest
from dataobj.validators import LengthValidator

from dataobj.validators import EmailValidator

from dataobj.validators.choice import ChoiceValidator


class TestChoiceValidator(object):
    @pytest.mark.parametrize('value',
                             [
                                 1, '2', '4', 5
                             ])
    def test_validate_ok(self, value):
        validator = ChoiceValidator(choices=[1, '2', '4', 5])
        assert validator.validate('value', value)

    @pytest.mark.parametrize('value',
                             [2, '3', 8, '12'])
    def test_validate_failed(self, value):
        validator = ChoiceValidator(choices=[1, '2', '4', 5])
        with pytest.raises(ValueError, match='Choice validation error on param `value={}`'.format(value)) as err:
            validator.validate('value', value)

    @pytest.mark.parametrize('value',
                             [2, 3, '5', 5])
    def test_validate_failed_with_error_handler(self, value):
        def error_handler(v):
            assert v == value

        validator = ChoiceValidator(choices=[1, '2', '4', 5], error_handler=error_handler)
        validator.validate('value', value)


class TestEmailValidator(object):
    @pytest.mark.parametrize('value',
                             [
                                 'mail@chris.com',
                                 'xyz@163.com',
                             ])
    def test_validate_ok(self, value):
        validator = EmailValidator()
        assert validator.validate('value', value) == value

    @pytest.mark.parametrize('value',
                             [
                                 'xyz@',
                                 'mail.com',
                                 'hello@xyz@foobar.com'
                             ])
    def test_validate_failed(self, value):
        validator = EmailValidator()
        with pytest.raises(ValueError, match='Email validation error on param `value={}`'.format(value)):
            validator.validate('value', value)

    @pytest.mark.parametrize('value',
                             ['xyz@',
                              'mail.com',
                              'hello@xyz@foobar.com'
                              ])
    def test_validate_failed_with_error_handler(self, value):
        def err_handler(v):
            assert v == value

        validator = EmailValidator(err_handler)
        validator.validate('value', value)


class TestLengthValidator(object):
    @pytest.mark.parametrize('value',
                             ['a',
                              'aa',
                              'aaa',
                              'b' * 100,
                              'x' * 100 * 100,
                              list(range(100))],
                             ids=['a', '2a', '3a',
                                  '100b', '10000x',
                                  'list'])
    def test_validate_without_length_specified(self, value):
        # 0 <= len < infinite
        validator = LengthValidator()
        assert validator.validate('value', value) == value

    @pytest.mark.parametrize('value',
                             ['abcd',
                              'abcdef',
                              'hello, world',
                              list(range(10))])
    def test_validate_with_min_length_ok(self, value):
        # 4 <= len < infinite
        validator = LengthValidator(min_length=4)
        assert validator.validate('value', value) == value

    @pytest.mark.parametrize('value', ['a',
                                       list(range(3)),
                                       '123',
                                       {1, 23, 4}])
    def test_validate_with_min_length_failed(self, value):
        # 4 <= len < infinite
        validator = LengthValidator(min_length=4)
        with pytest.raises(ValueError, match='Length validation error'):
            validator.validate('value', value)

    @pytest.mark.parametrize('value',
                             ['Hello',
                              'World',
                              ('ok', 'to', 'go')])
    def test_validate_with_max_length_ok(self, value):
        # 0 <= len <= 5
        validator = LengthValidator(max_length=5)
        assert validator.validate('value', value) == value

    @pytest.mark.parametrize('value', ['Hello, world',
                                       'Good to go',
                                       'Fine, it is ok to leave'])
    def test_validate_with_max_length_failed(self, value):
        # 0 <= len <= 5
        validator = LengthValidator(max_length=5)
        with pytest.raises(ValueError, match='Length validation error'):
            validator.validate('value', value)

    @pytest.mark.parametrize('value', ['Hello, world',
                                       list(range(10))])
    def test_validate_with_min_max_length_ok(self, value):
        # 5 <= len <= 12
        validator = LengthValidator(min_length=5, max_length=12)
        assert validator.validate('value', value) == value

    @pytest.mark.parametrize('value', [
        'Good',
        [1, 2],
        'Hello, world! Ok',
        'Oh, there is a giant monster'])
    def test_validate_with_min_max_length_failed(self, value):
        # 5 <= len <= 12
        validator = LengthValidator(min_length=5, max_length=12)
        with pytest.raises(ValueError, match='Length validation error'):
            validator.validate('value', value)

    @pytest.mark.parametrize('value', [
        'Good',
        [1, 2],
        'Hello, world! Ok',
        'Oh, there is a giant monster'
    ])
    def test_validate_with_min_max_length_failed_with_error_handler(self, value):
        def err_handler(v):
            assert v == value

        # 5 <= len <= 12
        validator = LengthValidator(min_length=5, max_length=12, error_handler=err_handler)
        validator.validate('value', value)


class TestNotNullValidator(object):
    def test_validate_ok(self):
        pass
