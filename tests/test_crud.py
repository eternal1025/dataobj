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
from dataobj import DataObject
from dataobj import DatetimeField
from dataobj import IntField
from dataobj import ListField
from dataobj import StrField

__version__ = '0.0.1'
__author__ = 'Chris'

logging.basicConfig(level=logging.DEBUG)

URL = 'mysql://root:chris@localhost:3306/yunos_new'


class CommonDao(object):
    @staticmethod
    def execute(sql, args):
        print(sql, args)
        return mysql_execute(sql, args=args, mysql_url=URL, debug=True)

    @staticmethod
    def query(sql, args):
        print(sql, args)
        return mysql_query(sql, args=args, mysql_url=URL, debug=True)


class FolderDataObject(DataObject):
    __table__ = 'folder'
    __dao_class__ = CommonDao

    folder_id = IntField(db_column='id', primary_key=True)
    name = StrField(db_column='name', default='新建文件夹')
    # icon_url = StrField(default='default.png')
    icon_url = ListField()
    create_at = DatetimeField(default=datetime.datetime.now)


class FolderChildDataObject(DataObject):
    __table__ = 'folder_child'
    __dao_class__ = CommonDao

    id = IntField(primary_key=True)
    folder_id = IntField()
    child_id = IntField()
    child_type = StrField()


if __name__ == '__main__':
    # folder = FolderDataObject(name="文件夹100",
    #                           icon_url='test.png')
    # print(folder.dump())
    # folder = FolderDataObject.load(2)
    # print(folder)
    # folder.update(name='测试哦')
    folder = FolderDataObject(icon_url=[(1, 2, 3, 4), ("xxx", "xxx")])
    folder.dump()
    for x in FolderDataObject.all():
        print(x)

    # for x in FolderDataObject.filter(folder_id__isnull=True):
    #     print(x)
