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


# 测试条件查询
def check_search(keyword):

    re_insert_data()

    with UsingAlchemy() as ua:

        # 多条件的列表组合
        query_filter = []
        if keyword:
            like_value = '%{}%'.format(keyword)

            # 查询 name 和 remark 字段里 包含查询关键词的记录
            query_filter.append(Product.name.like(like_value) | Product.remark.like(like_value))

        # 增加另一个查询条件作为测试
        query_filter.append(Product.isBuy == is_available)

        # 查找结果
        data_list = ua.session.query(Product).filter(*query_filter).all()
        print('-- 记录条数: {}'.format(len(data_list)))
        print('-- 该记录是: %s' % data_list[0].name)

if __name__ == '__main__':
    check_search(3)

