# python操作mysql之只看这篇就够了

## 初始化准备

安装pymysql 包
```bash
sudo pip3 install PyMysql 
```
然后在mysql里创建数据库名称为 my_test, 用户名/密码也是 my_test , 并创建 Product 表如下: 
```mysql
    DROP TABLE IF EXISTS `Product`;
    /*!40101 SET @saved_cs_client     = @@character_set_client */;
    /*!40101 SET character_set_client = utf8 */;
    CREATE TABLE `Product` (
      `id` int NOT NULL AUTO_INCREMENT,
      `name` varchar(40) NOT NULL,    /* 商品名称 */
      `remark` varchar(1000) NULL,
      `isBuy` int(1) DEFAULT 1, 	 /* 1: 在售 2:卖出 */
      `version` int(11) NOT null default 1000, 
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=utf8;
```

## 测试
pymysql 的代码还是很简单的, 以下代码分别为连接mysql 获得connection, 从connection 获得cursor 进行操作, 都是固定套路: 
```python
#! /usr/bin/python
# -*- coding: UTF-8 -*-

"""

    作者: 小肥巴巴
    简书: https://www.jianshu.com/u/db796a501972
    邮箱: imyunshi@163.com
    github: https://github.com/xiaofeipapa/python_example

    您可以任意转载, 恳请保留我作为原作者, 谢谢.


"""
import pymysql


host = 'localhost'
port = 3306
db = 'mysql_test'
user = 'mysql_test'
password = 'mysql_test'


# ---- 用pymysql 操作数据库
def get_connection():
    conn = pymysql.connect(host=host, port=port, db=db, user=user, password=password)
    return conn


def check_it():

    conn = get_connection()

    # 使用 cursor() 方法创建一个 dict 格式的游标对象 cursor
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 使用 execute()  方法执行 SQL 查询
    cursor.execute("select count(id) as total from Product")

    # 使用 fetchone() 方法获取单条数据.
    data = cursor.fetchone()

    print("-- 当前数量: %d " % data['total'])

    # 关闭数据库连接
    cursor.close()
    conn.close()


if __name__ == '__main__':
    check_it()
```

# pymysql 实战应用
## 使用with 优化操作代码
从以上代码可以看到, 如果每次都要打开连接, 关闭连接 .... 代码难看且容易出错. 最好的办法是用 python with 的方式来增加一个上下文管理器. 修改如下: 
```python
#! /usr/bin/python
# -*- coding: UTF-8 -*-

"""

    作者: 小肥巴巴
    简书: https://www.jianshu.com/u/db796a501972
    邮箱: imyunshi@163.com
    github: https://github.com/xiaofeipapa/python_example

    您可以任意转载, 恳请保留我作为原作者, 谢谢.

"""
import pymysql
from timeit import default_timer


host = 'localhost'
port = 3306
db = 'mysql_test'
user = 'mysql_test'
password = 'mysql_test'


# ---- 用pymysql 操作数据库
def get_connection():
    conn = pymysql.connect(host=host, port=port, db=db, user=user, password=password)
    return conn


# ---- 使用 with 的方式来优化代码
class UsingMysql(object):

    def __init__(self, commit=True, log_time=True, log_label='总用时'):
        """

        :param commit: 是否在最后提交事务(设置为False的时候方便单元测试)
        :param log_time:  是否打印程序运行总时间
        :param log_label:  自定义log的文字
        """
        self._log_time = log_time
        self._commit = commit
        self._log_label = log_label

    def __enter__(self):

        # 如果需要记录时间
        if self._log_time is True:
            self._start = default_timer()

        # 在进入的时候自动获取连接和cursor
        conn = get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        conn.autocommit = False

        self._conn = conn
        self._cursor = cursor
        return self

    def __exit__(self, *exc_info):
        # 提交事务
        if self._commit:
            self._conn.commit()
        # 在退出的时候自动关闭连接和cursor
        self._cursor.close()
        self._conn.close()

        if self._log_time is True:
            diff = default_timer() - self._start
            print('-- %s: %.6f 秒' % (self._log_label, diff))

    @property
    def cursor(self):
        return self._cursor

def check_it():

    with UsingMysql(log_time=True) as um:
        um.cursor.execute("select count(id) as total from Product")
        data = um.cursor.fetchone()
        print("-- 当前数量: %d " % data['total'])

if __name__ == '__main__':
    check_it()

```
程序运行结果如下: 
```bash
-- 当前数量: 0 
-- 用时: 0.002345 秒
```
用这种方式改写代码之后, 业务方法更精简. 并且加了参数方便进行单元测试和监控代码的运行时间, 不亦美哉. 
## 封装公用代码
现在新增一个pymysql_comm.py 类, 将连接代码和写好的UsingMysql 放进去, 代码如下: 
```python
#! /usr/bin/python
# -*- coding: UTF-8 -*-

"""

    作者: 小肥巴巴
    简书: https://www.jianshu.com/u/db796a501972
    邮箱: imyunshi@163.com
    github: https://github.com/xiaofeipapa/python_example

    您可以任意转载, 恳请保留我作为原作者, 谢谢.

"""
import pymysql
from timeit import default_timer


host = 'localhost'
port = 3306
db = 'mysql_test'
user = 'mysql_test'
password = 'mysql_test'


# ---- 用pymysql 操作数据库
def get_connection():
    conn = pymysql.connect(host=host, port=port, db=db, user=user, password=password)
    return conn


# ---- 使用 with 的方式来优化代码
class UsingMysql(object):

    def __init__(self, commit=True, log_time=True, log_label='总用时'):
        """

        :param commit: 是否在最后提交事务(设置为False的时候方便单元测试)
        :param log_time:  是否打印程序运行总时间
        :param log_label:  自定义log的文字
        """
        self._log_time = log_time
        self._commit = commit
        self._log_label = log_label

    def __enter__(self):

        # 如果需要记录时间
        if self._log_time is True:
            self._start = default_timer()

        # 在进入的时候自动获取连接和cursor
        conn = get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        conn.autocommit = False

        self._conn = conn
        self._cursor = cursor
        return self

    def __exit__(self, *exc_info):
        # 提交事务
        if self._commit:
            self._conn.commit()
        # 在退出的时候自动关闭连接和cursor
        self._cursor.close()
        self._conn.close()

        if self._log_time is True:
            diff = default_timer() - self._start
            print('-- %s: %.6f 秒' % (self._log_label, diff))

    @property
    def cursor(self):
        return self._cursor


```
新增一个 test.py 文件, 引入这个模块进行测试使用. 代码如下: 
```python
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


def check_it():

    with UsingMysql(log_time=True) as um:
        um.cursor.execute("select count(id) as total from Product")
        data = um.cursor.fetchone()
        print("-- 当前数量: %d " % data['total'])

if __name__ == '__main__':
    check_it()
```
后续的学习和开发都可以使用这个封装类, 用类似test.py的方式来写自己的业务代码, 更方便精简了. 

# 增删改查api
下面记录了最常用的增删改查分页等方法
## 新增单条记录
```python
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


def select_one(cursor):
    cursor.execute("select * from Product")
    data = cursor.fetchone()
    print("-- 单条记录: {0} ".format(data))


# 新增单条记录
def create_one():

    with UsingMysql(log_time=True) as um:
        sql = "insert into Product(name, remark) values(%s, %s)"
        params = ('男士双肩背包1', '这个是非常好的背包')
        um.cursor.execute(sql, params)

        # 查看结果
        select_one(um.cursor)

if __name__ == '__main__':
    create_one()


```
在上面代码里先增加了一条记录, 然后接着查看这条记录, 结果类似这样: 
```bash
-- 单条记录: {'id': 1003, 'name': '男士双肩背包1', 'isBuy': 1, 'remark': '这个是非常好的背包'} 
-- 用时: 0.002600 秒
```
顺便吐嘈下, 用1秒/0.0026 可计算得出并发数是 384.6 , 这表示无优化状态下每秒插入记录 384 条左右, 性能比较低. 
## 新增多条记录
一口气插入1000条记录, 同时加入查询方法, 如下: 
```python
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
```
在我的机器用时如下: 
```bash
-- 当前数量: 1000 
-- 用时: 0.097566 秒
```
勉强能接受. 现在用你的mysql 客户端查看数据库, 应该能看到1000条数据: 
![image.png](https://upload-images.jianshu.io/upload_images/4074593-2c3be7db36889f37.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

## 删除某条记录
为了方便测试, 顺便把查的方法也提前写出来了. 代码如下: 
```python
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

```
操作结果类似这样: 
```bash
--- 已找到名字为男士双肩背包0的商品. 
--- 已删除名字为男士双肩背包0的商品. 
--- 名字为男士双肩背包0的商品已经没有了
-- 用时: 0.015917 秒
```
## 修改记录
```python
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


def update_by_pk(cursor, name, pk):
    sql = "update Product set name = '%s' where id = %d" % (name, pk)

    cursor.execute(sql)


def select_one(cursor):
    sql = 'select * from Product'
    cursor.execute(sql)
    return cursor.fetchone()


def select_one_by_name(cursor, name):
    sql = 'select * from Product where name = %s'
    params = name
    cursor.execute(sql, params)
    data = cursor.fetchone()
    if data:
        print('--- 已找到名字为%s的商品. ' % data['name'])
    else:
        print('--- 名字为%s的商品已经没有了' % name)


# 修改记录
def check_update():

    with UsingMysql(log_time=True) as um:

        # 查找一条记录
        data = select_one(um.cursor)
        pk = data['id']
        print('--- 商品{0}: '.format(data))

        # 修改名字
        new_name = '单肩包'
        update_by_pk(um.cursor, new_name, pk)

        # 查看
        select_one_by_name(um.cursor, new_name)

if __name__ == '__main__':
    check_update()


```

这里记录了根据id修改记录的方法, 其他修改方式主要看sql 知识, 就不再赘述. 

## 查找
查找主要涉及pymysql 的fetchone(返回单条数据), fetchall(返回所有数据) . fetchone 上面已经写过了, 现在来看看fetchall 方法: 
```python
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

```
结果应该类似这样: 
```bash
-- 总数: 999
-- 总数: 0
-- 用时: 0.012355 秒
```
### 分页查询
分页查询主要是用了mysql 的limit 特性, 和pymysql 没太大关系, 代码如下: 
```python
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


def fetch_page_data(cursor, pk, page_size, skip):
    sql = 'select * from Product where id > %d limit %d,%d' % (pk, skip, page_size)
    cursor.execute(sql)
    data_list = cursor.fetchall()
    print('-- 总数: %d' % len(data_list))
    print('-- 数据: {0}'.format(data_list))
    return data_list


# 查找
def check_page():

    with UsingMysql(log_time=True) as um:

        page_size = 10
        pk = 500

        for page_no in range(1, 6):

            print('====== 第%d页数据' % page_no)
            skip = (page_no - 1) * page_size

            fetch_page_data(um.cursor, pk, page_size, skip)


if __name__ == '__main__':
    check_page()

```
上面列出了5页数据. 看起来大概是这样: 
![image.png](https://upload-images.jianshu.io/upload_images/4074593-88b060c0ed04c737.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


# 中级篇: 使用连接池和封装方法
经过一系列示例, 现在你应该会用pymysql 做最基本的增删改查分页了. 现在来看点高级点的功能: 更好的封装代码和使用数据库连接池. 
## 封装代码
我们发觉调用pymysql的代码都差不多, 其实可以挪到公用方法里去, 新增一个 pymysql_lib_1.py 文件, 实现UsingMysql 如下: 
```python
#! /usr/bin/python
# -*- coding: UTF-8 -*-

"""

    作者: 小肥巴巴
    简书: https://www.jianshu.com/u/db796a501972
    邮箱: imyunshi@163.com
    github: https://github.com/xiaofeipapa/python_example

    您可以任意转载, 恳请保留我作为原作者, 谢谢.

"""
import pymysql
from timeit import default_timer


host = 'localhost'
port = 3306
db = 'mysql_test'
user = 'mysql_test'
password = 'mysql_test'


# ---- 用pymysql 操作数据库
def get_connection():
    conn = pymysql.connect(host=host, port=port, db=db, user=user, password=password)
    return conn


# ---- 使用 with 的方式来优化代码
class UsingMysql(object):

    def __init__(self, commit=True, log_time=True, log_label='总用时'):
        """

        :param commit: 是否在最后提交事务(设置为False的时候方便单元测试)
        :param log_time:  是否打印程序运行总时间
        :param log_label:  自定义log的文字
        """
        self._log_time = log_time
        self._commit = commit
        self._log_label = log_label

    def __enter__(self):

        # 如果需要记录时间
        if self._log_time is True:
            self._start = default_timer()

        # 在进入的时候自动获取连接和cursor
        conn = get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        conn.autocommit = False

        self._conn = conn
        self._cursor = cursor
        return self

    def __exit__(self, *exc_info):
        # 提交事务
        if self._commit:
            self._conn.commit()
        # 在退出的时候自动关闭连接和cursor
        self._cursor.close()
        self._conn.close()

        if self._log_time is True:
            diff = default_timer() - self._start
            print('-- %s: %.6f 秒' % (self._log_label, diff))

    # ========= 一系列封装的业务方法

    # 返回 count
    def get_count(self, sql, params=None, count_key='count(id)'):
        self.cursor.execute(sql, params)
        data = self.cursor.fetchone()
        if not data:
            return 0
        return data[count_key]

    def fetch_one(self, sql, params=None):
        self.cursor.execute(sql, params)
        return self.cursor.fetchone()

    def fetch_all(self, sql, params=None):
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def fetch_by_pk(self, sql, pk):
        self.cursor.execute(sql, (pk,))
        return self.cursor.fetchall()

    def update_by_pk(self, sql, params=None):
        self.cursor.execute(sql, params)

    @property
    def cursor(self):
        return self._cursor


```
然后新增一个test2.py 文件进行测试, 如下: 
```python
#! /usr/bin/python
# -*- coding: UTF-8 -*-

"""

    作者: 小肥巴巴
    简书: https://www.jianshu.com/u/db796a501972
    邮箱: imyunshi@163.com
    github: https://github.com/xiaofeipapa/python_example

    您可以任意转载, 恳请保留我作为原作者, 谢谢.

"""
from pymysql_lib_1 import UsingMysql


def check_it():

    with UsingMysql(log_time=True) as um:
        sql = "select count(id) as total from Product"
        print("-- 当前数量: %d " % um.get_count(sql, None, 'total'))

if __name__ == '__main__':
    check_it()
```
可以看到业务代码精简了不少, 拼sql 和参数就好了, 其他调用方法都封装到了上下文管理器. 

## 使用连接池
在上面的使用过程中, 每个请求都会开启一个数据库连接. 如果连接数太多, 数据库很快就会报错. 如何调整数据库的连接数增加并发性能算是个比较有技术含量的话题, 我打算放到高级篇里再介绍. 现在这里要让你知道的是: 数据库这么返回连接是不行的, 必须要使用连接池. 

连接池代码当然不用自己动手, python的世界那么大~ 先安装DBUtils, 如下: 
```python
pip3 install DBUtils
```
然后新增 pymysql_lib.py , 增加代码如下: 
```python
#! /usr/bin/python
# -*- coding: UTF-8 -*-

"""

    作者: 小肥巴巴
    简书: https://www.jianshu.com/u/db796a501972
    邮箱: imyunshi@163.com
    github: https://github.com/xiaofeipapa/python_example

    您可以任意转载, 恳请保留我作为原作者, 谢谢.

"""
import pymysql
from timeit import default_timer
from DBUtils.PooledDB import PooledDB


class DMysqlConfig:
    """

        :param mincached:连接池中空闲连接的初始数量
        :param maxcached:连接池中空闲连接的最大数量
        :param maxshared:共享连接的最大数量
        :param maxconnections:创建连接池的最大数量
        :param blocking:超过最大连接数量时候的表现，为True等待连接数量下降，为false直接报错处理
        :param maxusage:单个连接的最大重复使用次数
        :param setsession:optional list of SQL commands that may serve to prepare
            the session, e.g. ["set datestyle to ...", "set time zone ..."]
        :param reset:how connections should be reset when returned to the pool
            (False or None to rollback transcations started with begin(),
            True to always issue a rollback for safety's sake)
        :param host:数据库ip地址
        :param port:数据库端口
        :param db:库名
        :param user:用户名
        :param passwd:密码
        :param charset:字符编码
    """

    def __init__(self, host, db, user, password, port=3306):
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password

        self.charset = 'UTF8'  # 不能是 utf-8
        self.minCached = 10
        self.maxCached = 20
        self.maxShared = 10
        self.maxConnection = 100

        self.blocking = True
        self.maxUsage = 100
        self.setSession = None
        self.reset = True


# ---- 用连接池来返回数据库连接
class DMysqlPoolConn:

    __pool = None

    def __init__(self, config):

        if not self.__pool:
            self.__class__.__pool = PooledDB(creator=pymysql,
                                             maxconnections=config.maxConnection,
                                             mincached=config.minCached,
                                             maxcached=config.maxCached,
                                             maxshared=config.maxShared,
                                             blocking=config.blocking,
                                             maxusage=config.maxUsage,
                                             setsession=config.setSession,
                                             charset=config.charset,
                                             host=config.host,
                                             port=config.port,
                                             database=config.db,
                                             user=config.user,
                                             password=config.password,
                                             )

    def get_conn(self):
        return self.__pool.connection()


# ========== 在程序的开始初始化一个连接池
host = 'localhost'
port = 3306
db = 'mysql_test'
user = 'mysql_test'
password = 'mysql_test'

db_config = DMysqlConfig(host, db, user, password, port)


g_pool_connection = DMysqlPoolConn(db_config)


# ---- 使用 with 的方式来优化代码
class UsingMysql(object):

    def __init__(self, commit=True, log_time=True, log_label='总用时'):
        """

        :param commit: 是否在最后提交事务(设置为False的时候方便单元测试)
        :param log_time:  是否打印程序运行总时间
        :param log_label:  自定义log的文字
        """
        self._log_time = log_time
        self._commit = commit
        self._log_label = log_label

    def __enter__(self):

        # 如果需要记录时间
        if self._log_time is True:
            self._start = default_timer()

        # 从连接池获取数据库连接
        conn = g_pool_connection.get_conn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        conn.autocommit = False

        self._conn = conn
        self._cursor = cursor
        return self

    def __exit__(self, *exc_info):
        # 提交事务
        if self._commit:
            self._conn.commit()
        # 在退出的时候自动关闭连接和cursor
        self._cursor.close()
        self._conn.close()

        if self._log_time is True:
            diff = default_timer() - self._start
            print('-- %s: %.6f 秒' % (self._log_label, diff))

    # ========= 一系列封装的业务方法

    # 返回 count
    def get_count(self, sql, params=None, count_key='count(id)'):
        self.cursor.execute(sql, params)
        data = self.cursor.fetchone()
        if not data:
            return 0
        return data[count_key]

    def fetch_one(self, sql, params=None):
        self.cursor.execute(sql, params)
        return self.cursor.fetchone()

    def fetch_all(self, sql, params=None):
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def fetch_by_pk(self, sql, pk):
        self.cursor.execute(sql, (pk,))
        return self.cursor.fetchall()

    def update_by_pk(self, sql, params=None):
        self.cursor.execute(sql, params)

    @property
    def cursor(self):
        return self._cursor
```
新增加的一大坨代码看起来很多, 其实只是增加了两个配置类. 同时在这里: 
```python
# ========== 在程序的开始初始化一个连接池
host = 'localhost'
port = 3306
db = 'mysql_test'
user = 'mysql_test'
password = 'mysql_test'

db_config = DMysqlConfig(host, db, user, password, port)


g_pool_connection = DMysqlPoolConn(db_config)
```
实例化了连接池.  后续的上下文管理器改从连接池获取连接, 其他代码都不变. 

把这个pymysql_lib 存好, 以后有机会慢慢增加/修改里面的各种fetch/update ... 方法, 这个文件会变成你的传家宝, 你会用它和mysql 打交道很多很多年... 

# 最后的严肃问题: raw sql ? 使用或放弃? 
从UsingMysql 可以看出代码优化到这个层面已经到头了. 可是那些什么insert 语句, update 语句还是要拼一大堆sql 字段, 怎么办? 这里有两个办法: 一个是思考一些代码生成技术, 根据各种参数自动组装sql, 这样下去这代码就会变成自己独有的orm了(年轻时我就这么干) . 另一个选择(也就是我现在的选择), 不用pymysql, 而是使用sqlalchemy ....  :-D :-D :-D 

我现在工作中很少用Mysql , 通常用到的时候都是接手别人的代码. 所以我一般这么做: 简单无性能瓶颈的业务代码, 我用sqlalchemy 不用动脑子. 有性能瓶颈的地方, 我用pymysql原生sql进行操作. 因为pymysql 网上很少成型的好文章, 所以我才写了这么一大坨进行总结. 

## sqlchemy 入门
新增一个 sqlal_comm.py 类, 代码如下: 
```python
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

```
这个文件分为两大部分: 上部分是 sqlalchemy 的固定套路: 拼接连接字符串, 进行连接初始化, 然后初始化数据库的表.  下部分是继续之前的上下文管理套路, 让代码编写更轻松点. 

新增一个test4.py 进行测试, 如下: 
```python
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
```
这个文件用两种方式来进行调用, 显然用了上下文管理的方式会更轻松点. 

## sqlalchemy 条件查询和分页
有一篇博客极好, 把增删改查总结得明明白白. 所以我也偷懒了, 在最后直接放出他的文章. 我这里来补充两个他没有写的: 条件查询和分页查询. 
### 条件查询
主要的业务场景就是: 用户传入多个参数, 要根据参数的不同构造不同的查询条件. 新增一个python文件, 如下: 
```python
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


```
这个文件的演示分两步: 
1) 删除原来数据库的数据, 插入10条新的测试数据. 这样能确保肯定有一条带关键字3的数据. 
2) 演示了如何组合查询条件进行查找, 其中有一个带or的查找条件. 从这个例子入手, 所有查询对你都不是难题了. 

程序运行结果应该类似这样: 
```bash
-- 总用时: 0.009106 秒
-- 记录条数: 1
-- 该记录是: 双肩包3
-- 总用时: 0.001323 秒
```

## 分页查找
增加一个新的python文件, 代码如下: 
```python
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


```
可以看到分页查找就是在获取列表之前调用limit 和 offset 方法, 也就是这句: 
```python
data_list = ua.session.query(Product).filter(*query_filter).limit(page_size).offset(offset).all()
```
所以 , 也是很简单的. 

## sqlalchemy 增删改查总结
这篇文章写得很好了, 看这里吧: [https://www.cnblogs.com/pycode/p/mysql-orm.html](https://www.cnblogs.com/pycode/p/mysql-orm.html)

# 最后, 这次真的是最后了
python 使用mysql 的基础知识就总结到这了. 等有时间我再写关于事务锁和优化并发性能的高级篇. 

少年, 给个star 再走啊~~