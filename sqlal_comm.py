#! /usr/bin/python
# -*- coding: UTF-8 -*-

"""

    作者: 小肥巴巴
    简书: https://www.jianshu.com/u/db796a501972
    邮箱: imyunshi@163.com
    github: https://github.com/xiaofeipapa/python_example

    您可以任意转载, 恳请保留我作为原作者, 谢谢.

"""


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Index, Text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from timeit import default_timer


host = 'localhost'
port = 3306
db = 'mysql_test'
user = 'mysql_test'
password = 'mysql_test'


g_mysql_url = 'mysql+pymysql://%s:%s@%s:%d/%s' % (user, password, host, port, db)


engine = create_engine(g_mysql_url)

Base = declarative_base()


class Product(Base):
    __tablename__ = 'Product'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(40))
    remark = Column(String(1000), nullable=True)
    isBuy = Column(Integer, default=1)

Base.metadata.create_all(engine)  #创建表

Session = sessionmaker(bind=engine)

# =============== 以上为初始化数据库和表


# ---- 使用 with 的方式来优化代码
class UsingAlchemy(object):

    def __init__(self, commit=True, log_time=True, log_label='总用时'):
        """

        :param commit: 是否在最后提交事务(设置为False的时候方便单元测试)
        :param log_time:  是否打印程序运行总时间
        :param log_label:  自定义log的文字
        """
        self._log_time = log_time
        self._commit = commit
        self._log_label = log_label
        self._session = Session()

    def __enter__(self):

        # 如果需要记录时间
        if self._log_time is True:
            self._start = default_timer()

        return self

    def __exit__(self, *exc_info):
        # 提交事务
        if self._commit:
            self._session.commit()

        if self._log_time is True:
            diff = default_timer() - self._start
            print('-- %s: %.6f 秒' % (self._log_label, diff))

    @property
    def session(self):
        return self._session
