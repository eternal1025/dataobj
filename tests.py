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


class FolderChildDataObject(DataObject):
    __table__ = 'folder_child'
    __dao_class__ = CommonDao

    id = IntField(primary_key=True)
    folder_id = IntField()
    child_id = IntField()
    child_type = StrField()


if __name__ == '__main__':
    # folder = FolderDataObject(name="文件夹1",
    #                           icon_url='test.png')
    # print(folder.dump())
    folder = FolderDataObject.load(1)
    child = FolderChildDataObject(child_id=1, child_type='app',
                                  folder=folder)
    print(child.dump())
