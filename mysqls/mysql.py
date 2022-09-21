import pymysql
from config import *
from timeit import default_timer
from dbutils.pooled_db import PooledDB


class MysqlConfig():
    """
            :param mincached:连接池中空闲连接的初始数量
            :param maxcached:连接池中空闲连接的最大数量
            :param maxshared:共享连接的最大数量
            :param maxconnections:创建连接池的最大数量
            :param blocking:超过最大连接数量时候的表现，为True等待连接数量下降，为false直接报错处理
            :param maxusage:单个连接的最大重复使用次数
            :param host:数据库ip地址
            :param port:数据库端口
            :param db:库名
            :param user:用户名
            :param passwd:密码
            :param charset:字符编码
        """

    def __init__(self, host, db, user, password, port):
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.password = password

        self.charset = charset
        self.minCached = minCached
        self.maxCached = maxCached
        self.maxShared = maxShared
        self.maxConnection = maxConnection

        self.blocking = blocking
        self.maxUsage = maxUsage
        self.setSession = setSession
        self.reset = reset


class PoolConn:
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


host = host
port = port
db = db
user = user
password = password

db_config = MysqlConfig(host=host, db=db, user=user, password=password, port=port)

pool_connection = PoolConn(db_config)


class ConnectMysql(object):
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
        # 记录时间
        if self._log_time is True:
            self._start = default_timer()
        # 连接
        conn = pool_connection.get_conn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        conn.autocommit = False

        self._conn = conn
        self._cursor = cursor
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 提交事务
        if self._commit:
            self._conn.commit()
        # 在退出的时候自动关闭连接和cursor
        self._cursor.close()
        self._conn.close()

        if self._log_time is True:
            diff = default_timer() - self._start
            print('-- %s: %.6f 秒' % (self._log_label, diff))

    def get_count(self, sql, params=None, count_key='count(id)'):
        self.cursor.execute(sql, params)
        data = self.cursor.fetchone()
        if not data:
            return 0
        return data[count_key]

    def find_one(self, sql, params=None):
        self.cursor.execute(sql, params)
        return self.cursor.fetchone()

    def find_all(self, sql, params=None):
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def find_by_pk(self, sql, pk):
        self.cursor.execute(sql, (pk,))
        return self.cursor.fetchall()

    def update_by_pk(self, sql, params=None):
        self.cursor.execute(sql, params)

    def insert(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def saveOrUpdate(self, sql, val):
        self.cursor.executemany(sql, val)

    def execute(self,sql,params=None):
        '''

        :param sql:字符串类型，sql语句
        :param params:sql语句中要替换的参数"select %s from tab where id=%s" 其中的%s就是参数
        :return:
        '''
        count = 0
        try:
            # count : 为改变的数据条数
            if params:
                count = self.cursor.execute(sql,params)
            else:
                count = self.cursor.execute(sql)
            # self._conn.commit()
        except Exception as e:
            pass
        return self.cursor.fetchall()

    @property
    def cursor(self):
        return self._cursor
