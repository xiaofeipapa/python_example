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

is_available = 1


# 重新插入数据
def re_insert_data():

    with UsingAlchemy() as ua:

        # 删除所有数据
        ua.session.query(Product).filter(Product.id > 0).delete()

        data_list = []
        for i in range(0, 10):

            data = Product()
            data.name = '双肩包%d' % i
            data.remark = '双肩包%d' % i
            data.isBuy = is_available
            data_list.append(data)

        # 批量增加数据
        ua.session.add_all(data_list)


# 测试分页查找
def check_search(page_no, page_size):

    re_insert_data()

    with UsingAlchemy() as ua:

        # 多条件的列表组合
        query_filter = list()

        # 增加另一个查询条件作为测试
        query_filter.append(Product.isBuy == is_available)

        offset = (page_no - 1) * page_size

        # 查找结果
        data_list = ua.session.query(Product).filter(*query_filter).limit(page_size).offset(offset).all()
        print('=== 记录条数: {}'.format(len(data_list)))
        for data in data_list:
            print('-- 记录: ' + data.name)

if __name__ == '__main__':

    page_size = 5
    for page_no in range(1, 3):
        check_search(page_no, page_size)


