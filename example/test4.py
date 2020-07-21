#! /usr/bin/python
# -*- coding: UTF-8 -*-

"""

    作者: 小肥巴巴
    简书: https://www.jianshu.com/u/db796a501972
    邮箱: imyunshi@163.com
    github: https://github.com/xiaofeipapa/python_example

    您可以任意转载, 恳请保留我作为原作者, 谢谢.

"""

from sqlal_comm import Session, Product, UsingAlchemy


# 测试获取一条记录
def check_it():

    session = Session()

    result = session.query(Product).first()
    if result is None:
        session.commit()
        return None

    session.commit()
    session.close()
    print('-- 得到记录: {0}'.format(result))


# 测试获取一条记录
def check_it_2():

    with UsingAlchemy() as ua:

        result = ua.session.query(Product).first()
        print('-- 得到记录: {0}'.format(result))

if __name__ == '__main__':
    check_it()
    check_it_2()