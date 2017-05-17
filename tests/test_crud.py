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

from dataobj import IntField, DatetimeField
from dataobj import Model
from dataobj import StrField

__version__ = '0.0.1'
__author__ = 'Chris'

logging.basicConfig(level=logging.DEBUG)

URL = 'mysql://root:chris@localhost:3306/yunos_new'


class CommonDao(object):
    @staticmethod
    def execute(sql, args):
        # print("execute:", sql, args)
        return mysql_execute(sql, args=args, mysql_url=URL, debug=True)

    @staticmethod
    def query(sql, args):
        # print("query:", sql, args)
        return mysql_query(sql, args=args, mysql_url=URL, debug=True)


class Folder(Model):
    folder_id = IntField(db_column='id', primary_key=True, auto_increment=True)
    name = StrField(db_column='name', default='新建文件夹', max_length=255)
    icon_url = StrField(not_null=False, max_length=1024)
    create_at = DatetimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'folder'
        dao_class = CommonDao


def test_query():
    print(Folder.objects.count())
    results = Folder.objects.all().order_by("folder_id").limit(0)
    print("Length of results: {}".format(len(results)))
    print("First item of results: {}".format(results.first()))
    print("Last item of results: {}".format(results.last()))
    print("List slicing: {}".format(results[:5]))

    print()
    print('Change sort order')
    results = Folder.objects.all().order_by("folder_id", descending=True).limit(10)
    print("Length of results: {}".format(len(results)))
    print("First item of results: {}".format(results.first()))
    print("Last item of results: {}".format(results.last()))
    print("List slicing: {}".format(results[:5]))

    print()
    print("Iterate each item")
    for item in results[::3]:
        print(item)

    print()
    print(Folder.objects.filter(name__endswith=0).order_by("folder_id")[4])

    # Last folder
    print()
    print()
    print('Last folder')
    last_folder = Folder.objects.all().order_by('folder_id').last()
    print(last_folder)

    # Act like a dict
    print(last_folder['name'])
    print(last_folder['icon_url'])

    last_folder['name'] = '测试文件夹—字典赋值'
    print(last_folder, len(last_folder))
    print('folder_id' not in last_folder)

    results = (Folder.objects.filter_with_field_names("folder_id").order_by("folder_id"))
    print(results[:10])
    print(len(results))
    print(results.first())

    print(Folder.objects.limit(1).first())

    print(list(Folder.objects.filter(name__startswith="你好")))


def test_dump_new(start=10, how_many=50):
    for index in range(start, how_many):
        folder = Folder()
        folder.name = '新建文件夹_{}'.format(index)
        folder.icon_url = "https://img.moviewisdom.cn/folder_icon_{}.png".format(index)
        folder.dump()


def test_update():
    folder = Folder.objects.all().order_by("folder_id", descending=True).first()
    print(folder)

    print(folder.update(name="测试更新-文件夹_{}".format(folder.folder_id)))
    folder = Folder.objects.all().order_by("folder_id", descending=True).first()
    print(folder)


def test_delete():
    folder = Folder.objects.all().order_by("folder_id", descending=True).first()
    print(folder)

    print(folder.delete())
    folder = Folder.objects.all().order_by("folder_id", descending=True).first()
    print(folder)


if __name__ == '__main__':
    # test_dump_new()
    # test_update()
    # test_delete()
    test_query()
