# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : test_sqlbuilder.py
# Date   : 2017-05-11 15-37
# Version: 0.0.1
# Description: description of this file.

import pandas as pd
from db_util import mysql_query
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
PROD_SAFE_DB_URI = 'mysql://zhangwenchen:m32hyAq23@192.168.2.235:3306/safe_db?charset=utf8'


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


def test_group_by():
    sql, args = SQLArgsBuilder('sum_film_ci_day_time_slice_box_peoples_sessions',
                               select='area_id, true_sessionDate, SUM(sessions) AS sessions, film_belong_id',
                               where={'film_belong_id__range': (5000, 5010)},
                               group_by='area_id, true_sessionDate',
                               limit=1000,
                               descending_order_by='film_belong_id').sql_args
    print(sql)
    print(pd.read_sql(sql, PROD_SAFE_DB_URI, params=args))


def test_in():
    sql, args = SQLArgsBuilder('sum_film_ci_day_time_slice_box_peoples_sessions',
                               select='area_id, true_sessionDate, SUM(sessions) AS sessions, film_belong_id',
                               where={'film_belong_id__in': [5001, 5000, 5002]},
                               group_by='area_id, true_sessionDate',
                               limit=10000,
                               descending_order_by='film_belong_id').sql_args
    print(sql)
    print(args)
    print(pd.read_sql(sql, PROD_SAFE_DB_URI, params=args))
    # print(pd.DataFrame.from_records(mysql_query(sql, args, mysql_url=PROD_SAFE_DB_URI, debug=True)))


def main():
    # test_select_sql()
    # test_insert_sql()
    # test_update_sql()
    # test_delete_sql()
    # test_sql_conditions()
    # test_group_by()
    test_in()


if __name__ == '__main__':
    main()
