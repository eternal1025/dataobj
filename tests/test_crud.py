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
from dataobj import Model
from dataobj import DatetimeField
from dataobj import IntField
from dataobj import ListField
from dataobj import StrField

__version__ = '0.0.1'
__author__ = 'Chris'

logging.basicConfig(level=logging.ERROR)

URL = 'mysql://root:chris@localhost:3306/yunos_new'


class CommonDao(object):
    @staticmethod
    def execute(sql, args):
        print("execute:", sql, args)
        return mysql_execute(sql, args=args, mysql_url=URL, debug=True)

    @staticmethod
    def query(sql, args):
        print("query:", sql, args)
        return mysql_query(sql, args=args, mysql_url=URL, debug=True)


class Folder(Model):
    folder_id = IntField(db_column='id', primary_key=True, auto_increment=True)
    name = StrField(db_column='name', default='新建文件夹', max_length=255)
    icon_url = StrField(not_null=True, max_length=1024)
    create_at = DatetimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'folder'
        dao_class = CommonDao


if __name__ == '__main__':
    for folder in Folder.objects.all().order_by('folder_id', descending=True).limit(3):
        print(folder)
    print()
    print(Folder.objects.all().order_by('name').limit(1).last())
    # print(Folder.objects.all().first())

    # 新增
    folder = Folder(name='新建测试文件夹',
                    icon_url='https://baidu.com/icon.png')
    print(folder)
    print(folder.dump())

    folder_id = folder.folder_id

    # 修改
    folder = Folder.objects.get(folder_id=folder_id)
    print(folder)

    folder.icon_url = 'https://moviewisdom.cn'
    print(folder.update())

    # 修改方式 2
    folder = Folder.objects.get(folder_id=folder_id)
    print(folder)

    print(folder.update(icon_url='https://moviewisdom.cn/change_url'))

    # 删除
    folder = Folder.objects.get(folder_id=folder_id)
    folder.delete()
