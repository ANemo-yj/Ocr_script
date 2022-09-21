#  mysql配置
host = '192.168.1.120'
port = 3306
db = 'dc'
user = 'dc'
password = 'dc!Hsit@2021'

charset = 'UTF8'
minCached = 10  # 连接池中空闲连接的初始数量
maxCached = 20  # 连接池中空闲连接的最大数量
maxShared = 10  # 共享连接的最大数量
maxConnection = 100  # 创建连接池的最大数量
blocking = True  # 超过最大连接数量时候的表现，为True等待连接数量下降，为false直接报错处理
maxUsage = 100  # 单个连接的最大重复使用次数
setSession = None
reset = True    # 返回重置连接

