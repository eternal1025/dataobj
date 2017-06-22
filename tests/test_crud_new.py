# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: MIT License
# File   : test_crud_new.py
# Date   : 2017-06-21 09-35
# Version: 0.1
# Description: description of this file.

import logging
from dataobj import Model, IntField, StrField
from dbutil import ConnectionRouter

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'chris',
    'database': 'test',
    'port': 3306
}

db_config_url = 'mysql://root:chris@localhost:3306/test?charset=utf8'

logging.basicConfig(level=logging.DEBUG)


class User(Model):
    id = IntField(primary_key=True, auto_increment=True)
    name = StrField(not_null=True)
    age = IntField(not_null=True)

    class Meta:
        table_name = 'user'
        connection = ConnectionRouter(db_config)


def test_insert(conn):
    names = 'Chris Mike Pike'.split()
    ages = '20 30 40'.split()

    for name, age in zip(names, ages):
        user = User(name=name, age=age)
        print('新增：', user.dump(conn))
        print(user)


def test_delete(conn):
    print('删除')
    for _ in range(User.objects.count()):
        User.objects.all(conn).first().delete()


def test_query(conn):
    for u in User.objects.all(conn).order_by('id', descending=True).limit(5):
        print(u)


def test_update(conn):
    print('更新')
    user = User.objects.all(conn).last()
    print(user.update(conn, name='ABC'))
    print(User.objects.all(conn).last())


def test_crud(conn):
    test_insert(conn)
    test_update(conn)
    test_query(conn)
    test_delete(conn)


if __name__ == '__main__':
    # 使用默认配置
    test_crud(None)

    # 使用 url 格式配置
    test_crud(db_config_url)

    # 使用字典配置
    test_crud(db_config)

    # 使用一个连接器对象
    test_crud(ConnectionRouter(db_config_url))

    # 使用一个 callable 对象
    test_crud(lambda: db_config)
    test_crud(lambda: db_config_url)
