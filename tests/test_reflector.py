# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : test_reflector.py
# Date   : 2017-05-19 09-52
# Version: 0.0.1
# Description: description of this file.

import logging
from pprint import pprint

from db_util import mysql_execute
from db_util import mysql_query

from dataobj.reflector import MySQLTableReflector

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


def test_check_type_mappings():
    r = MySQLTableReflector(CommonDao)
    # print(r.get_type_mappings())
    print(r.reflect('folder', 'FolderDataObject',))
    print(r.reflect('app', 'AppDataObject'))
    print(r.reflect('app_score'))
    print(r.reflect('dock_child'))
    print(r.reflect('workspace_child').field_classes)
    print(r.tables_can_be_reflected)


if __name__ == '__main__':
    test_check_type_mappings()