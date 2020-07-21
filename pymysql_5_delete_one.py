#! /usr/bin/python
# -*- coding: UTF-8 -*-

"""

    作者: 小肥巴巴
    简书: https://www.jianshu.com/u/db796a501972
    邮箱: imyunshi@163.com
    github: https://github.com/xiaofeipapa/python_example

    您可以任意转载, 恳请保留我作为原作者, 谢谢.

"""
from pymysql_comm import UsingMysql


def delete_one(cursor, name):
    sql = 'delete from Product where name = %s'
    params = name
    cursor.execute(sql, params)
    print('--- 已删除名字为%s的商品. ' % name)


def select_one(cursor):
    sql = 'select * from Product'
    cursor.execute(sql)
    data = cursor.fetchone()
    print('--- 已找到名字为%s的商品. ' % data['name'])
    return data['name']


def select_one_by_name(cursor, name):
    sql = 'select * from Product where name = %s'
    params = name
    cursor.execute(sql, params)
    data = cursor.fetchone()
    if data:
        print('--- 已找到名字为%s的商品. ' % data['name'])
    else:
        print('--- 名字为%s的商品已经没有了' % name)


# 删除单条记录
def check_delete_one():

    with UsingMysql(log_time=True) as um:

        # 查找一条记录
        name = select_one(um.cursor)

        # 删除之
        delete_one(um.cursor, name)

        # 查看还在不在?
        select_one_by_name(um.cursor, name)

if __name__ == '__main__':
    check_delete_one()

