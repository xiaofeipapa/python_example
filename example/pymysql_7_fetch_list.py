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


def fetch_list_by_filter(cursor, pk):
    sql = 'select * from Product where id > %d' % pk
    cursor.execute(sql)
    data_list = cursor.fetchall()
    print('-- 总数: %d' % len(data_list))
    return data_list


# 查找
def fetch_list():

    with UsingMysql(log_time=True) as um:

        # 查找id 大于800的记录
        data_list = fetch_list_by_filter(um.cursor, 800)

        # 查找id 大于 10000 的记录
        data_list = fetch_list_by_filter(um.cursor, 10000)

if __name__ == '__main__':
    fetch_list()