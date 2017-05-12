# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : test_sqlbuilder.py
# Date   : 2017-05-11 15-37
# Version: 0.0.1
# Description: description of this file.

from dataobj.sqlargs import SQLArgsBuilder

folder_fields = ['name', 'size']
row = {
    'name': 'demo_folder',
    'size': 20 * 20,
    'icon': 'default.png',
}

condition = {
    'name__contains': 'demo'
}


def test_select_sql():
    print(SQLArgsBuilder('folder', select='*'))
    print(SQLArgsBuilder('folder', select=folder_fields, where=condition))
    print(SQLArgsBuilder('folder', select=row, where=condition))
    print()


def test_insert_sql():
    print(SQLArgsBuilder('folder', insert=folder_fields))
    print(SQLArgsBuilder('folder', insert=row))
    print()


def test_update_sql():
    print(SQLArgsBuilder('folder', update=row, where=condition))
    print()


def test_delete_sql():
    print(SQLArgsBuilder('folder', delete='', where=condition))
    print()


def test_sql_conditions():
    # default condition is `eq`
    print(SQLArgsBuilder('folder', where={'size__eq': 30, 'age': 20}))
    print(SQLArgsBuilder('folder', where={'size__lt': 10, 'size__lte': 10}))
    print(SQLArgsBuilder('folder', where={'age__gt': 20, 'age__gte': 20}))
    print(SQLArgsBuilder('folder', where={'name__contains': 'hello',
                                          'name__startswith': 'hello',
                                          'name__endswith': 'hello'}))
    print(SQLArgsBuilder('folder', where={'size__isnull': True, 'name__isnull': False}))


def main():
    test_select_sql()
    test_insert_sql()
    test_update_sql()
    test_delete_sql()
    test_sql_conditions()


if __name__ == '__main__':
    main()
