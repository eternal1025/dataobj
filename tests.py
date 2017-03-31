# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : tests.py
# Date   : 2017-03-13 15-25
# Version: 0.0.1
# Description: description of this file.

import decimal
import logging
import datetime
from db_util import mysql_query, mysql_execute
from dataobj import DataObject, IntField, StrField, DatetimeField

__version__ = '0.0.1'
__author__ = 'Chris'

logging.basicConfig(level=logging.DEBUG)

URL = 'mysql://root:chris@localhost:3306/yunos_new'


class CommonDao(object):
    def __init__(self):
        pass

    @staticmethod
    def execute(sql):
        return mysql_execute(sql, mysql_url=URL)

    @staticmethod
    def query(sql):
        return mysql_query(sql, mysql_url=URL)


class FolderDataObject(DataObject):
    __table__ = 'folder'
    __dao_class__ = CommonDao

    folder_id = IntField(db_column='id', primary_key=True)
    name = StrField(default='新建文件夹')
    icon_url = StrField(default='default.png')
    create_at = DatetimeField(default=datetime.datetime.now)


if __name__ == '__main__':
    # Create a new object
    folder = FolderDataObject()
    folder.name = 'name'
    print(folder.dump())
    print(folder)
    # print(folder)
    # #
    folder_2 = FolderDataObject(name='新建测试文件夹-2017-2')
    print(folder_2)
    # #
    # # # Save folder object
    folder_2.dump()
    print(folder_2)
    # print(FolderDataObject.load(7))

    # Load a folder object from database
    folder = FolderDataObject.load(2)
    # print('{!r}'.format(folder))

    # Rename folder
    folder.name = '新建文件夹-改名'
    print(folder)

    # Sync it to db
    folder.update()
    print(folder)

    # Delete a folder
    folder.delete()

    # Filter
    for f in FolderDataObject.all():
        print(f)
