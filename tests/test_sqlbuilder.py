# -*-coding: utf-8-*-
# Author : Christopher Lee
# License: Apache License
# File   : test_sqlbuilder.py
# Date   : 2017-05-11 15-37
# Version: 0.0.1
# Description: description of this file.

from dataobj.sqlargs import SQLArgsBuilder


def main():
    fields = ['name', 'age', 'place']
    data = {
        'name': 'Chris',
        'age': 24,
        'place': 'Beijing',
        'weight': 100
    }

    conditions = {
        'name': 'Chris',
        'age__gt': 20
    }

    print(SQLArgsBuilder('test', select=fields, where=conditions))
    print(SQLArgsBuilder('test', insert=data))
    print(SQLArgsBuilder('test', update=data, where=conditions))
    print(SQLArgsBuilder('test', delete=''))



if __name__ == '__main__':
    main()
