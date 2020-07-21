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


def get_count(cursor):
    cursor.execute("select count(id) as total from Product")

    # 使用 fetchone() 方法获取单条数据.
    data = cursor.fetchone()

    print("-- 当前数量: %d " % data['total'])


def delete_all(cursor):
    cursor.execute("delete from Product")


# 插入 1000 条记录
def create_many():

    with UsingMysql(log_time=True) as um:

        # 清空之前的测试记录
        delete_all(um.cursor)

        for i in range(0, 1000):

            sql = "insert into Product(name, remark) values(%s, %s)"
            params = ('男士双肩背包%d' % i, '这个是非常好的背包%d' %i)
            um.cursor.execute(sql, params)

        # 查看结果
        get_count(um.cursor)

if __name__ == '__main__':
    create_many()

