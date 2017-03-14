# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : tests.py
# Date   : 2017-03-13 15-25
# Version: 0.0.1
# Description: description of this file.

import logging
import datetime
from db_util import mysql_query, mysql_execute
from dataobj import DataObject, IntField, StrField, DatetimeField, BoolField

__version__ = '0.0.1'
__author__ = 'Chris'

logging.basicConfig(level=logging.DEBUG)

URL = 'mysql://root:chris@localhost:3306/yunos_new'


class FolderDataObject(DataObject):
    __table__ = 'folder'

    folder_id = IntField(db_column='id', primary_key=True)
    name = StrField(default='新建文件夹')
    icon_url = StrField(default='default.png')
    create_at = DatetimeField(default=datetime.datetime.now)
    is_sub_folder = BoolField(db_column='is_sub', default=True)

    @staticmethod
    def _query(sql):
        print('Query sql: {}'.format(sql))
        return mysql_query(sql, mysql_url=URL)

    @staticmethod
    def _execute(sql):
        print('Execute sql: {}'.format(sql))
        return mysql_execute(sql, mysql_url=URL)


if __name__ == '__main__':
    # f = FolderDataObject.load(19)
    # print(f)
    #
    # # f.delete()
    # for f in FolderDataObject.filter(name='兴趣'):
    #     print(f)
    f = FolderDataObject(name='测试文件夹')
    f.save()
