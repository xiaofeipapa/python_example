#! /usr/bin/python
# -*- coding: UTF-8 -*-

"""

    作者: 小肥巴巴
    简书: https://www.jianshu.com/u/db796a501972
    邮箱: imyunshi@163.com
    github: https://github.com/xiaofeipapa/python_example

    您可以任意转载, 恳请保留我作为原作者, 谢谢.

"""
from pymysql_lib import UsingMysql


def check_it():

    with UsingMysql(log_time=True) as um:
        sql = "select count(id) as total from Product"
        print("-- 当前数量: %d " % um.get_count(sql, None, 'total'))

if __name__ == '__main__':
    check_it()