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
import threading
from random import randint



# 模拟用户行为, 仅仅是查看数据库连接
def mock_user_action(name):

    log_label = '%s 查看了数据库' % name

    with UsingMysql(log_time=False) as um:

        um.cursor.execute("update Product set name = '%s' from Product")
        data = um.cursor.fetchone()

        if not data:
            print('-- ')
            return




def check_access():

    user_count = 100000                # 模拟用户数

    # 模拟用户抢商品
    for i in range(0, user_count):
        user_name = '用户-%d' % i
        thread = threading.Thread(target=mock_user_action, args=(user_name,))
        thread.start()


if __name__ == '__main__':
    check_access()

