# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : test_model.py
# Date   : 2017-05-16 15-05
# Version: 0.0.1
# Description: description of this file.

from dataobj.model import Model, IntField, StrField, DecimalField, ListField

__version__ = '0.0.1'
__author__ = 'Chris'


class Dao(object):
    @staticmethod
    def execute(sql, args):
        print(sql, args)
        return 0

    @staticmethod
    def query(sql, args):
        print(sql, args)
        return []


class Book(Model):
    id = IntField(primary_key=True, db_column='book_id', auto_increment=False)
    name = StrField(default='Demo book')
    author = StrField()
    price = DecimalField(default=100.0)

    class Meta:
        table_name = 'custom_book'
        dao_class = Dao

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.custom_field = 100


if __name__ == '__main__':
    import copy

    book = Book(id="10")
    book.author = ["Chris", "You"]
    # print(book.author)
    # print(book.dict_data)
    book.dump()

    # print(Book.from_raw_dict(name="Chris", book_id=100, author="100"))
    # print(book.id, type(book.id))
    # print(type(book.price))
    # print(book.dict_data)
    # print(book.dump())
    # print(book.delete())
    # print(book.update())
    #
    # manger = Book.objects
    # print(manger, id(manger), manger.__dict__)
    #
    # results = Book.objects.filter(name__startswith='chris').order_by("name").limit(100)[:]
    #
    # new_manager = copy.deepcopy(manger)
    # print(new_manager, id(new_manager), new_manager.__dict__)
    #
    # for x in Book.objects.limit(10):
    #     print(x)
    #
    # # 检查字段是否存在于 Book Model 中
    # print('id' in Book)
    # print('id' in book)
    # print('names' in Book)
