# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : test_model.py
# Date   : 2017-05-16 15-05
# Version: 0.0.1
# Description: description of this file.

from dataobj.model import Model, IntField, StrField, DecimalField

__version__ = '0.0.1'
__author__ = 'Chris'


class Dao(object):
    @staticmethod
    def execute(sql, args):
        return 0

    @staticmethod
    def query(sql, args):
        return []


class Book(Model):
    id = IntField(primary_key=True, db_column='book_id', auto_increment=False)
    name = StrField(default='Demo book')
    author = StrField(max_length=5)
    price = DecimalField(default=100.0)

    class Meta:
        table_name = 'custom_book'
        dao_class = Dao

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.custom_field = 100


if __name__ == '__main__':
    book = Book(id="10")
    book.author = 'Chris'
    # print(book.id, type(book.id))
    # print(type(book.price))
    # print(book.dict_data)
    # print(book.value_of_primary_key)
    print(book.dump())
    print(book.delete())
    print(book.update())

    for x in Book.objects.filter(name__startswith='chris').limit(10):
        print(x)
