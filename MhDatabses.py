import pymysql

# 类 MhDatabases
# 作者：陶一丁
# 作用：提供数据库操作函数
# 最后修改时间：2019.8.22
class MhDatabases:
    def __init__(self):
        self.host = "139.217.130.233"  # 微软Azure服务器IP
        self.port = 3306
        self.db = "macrohard"          # 数据库名称
        self.user = "root"
        self.passwd = "password"
        self.charset = 'utf8'

# 函数 connection
# 作者：陶一丁
# 作用：数据库连接
# 最后修改时间：2019.8.22
    def connection(self):
        self.conn = pymysql.connect(host=self.host,
                                    port=self.port,
                                    db=self.db,
                                    user=self.user,
                                    passwd=self.passwd,
                                    charset=self.charset)
        self.cls = self.conn.cursor()

# 函数 free
# 作者：陶一丁
# 作用：释放数据库连接
# 最后修改时间：2019.8.22
    def free(self):
        self.cls.close()
        self.conn.close()

# 函数 executeUpdate
# 作者：陶一丁
# 作用：数据库增删改
# 最后修改时间：2019.8.22
    def executeUpdate(self, sql, param=[]):
        try:
            self.connection()
            row = self.cls.execute(sql, param)
            self.conn.commit()
        except Exception as e:
            print(e)
        finally:
            self.free()
        return row

    # 函数 executeTable
    # 作者：王明
    # 作用：数据库建表
    # 最后修改时间：2019.8.27
    def executecreatetable(self, tname):
        try:
            self.connection()
            row = self.cls.execute("create table  if not exists `%s`(operation int,gid varchar(20),gname varchar(20),gnumber int,gprice double,gtotal double,otime varchar(20))"%(tname))
            self.conn.commit()
        except Exception as e:
            print(e)
        finally:
            self.free()
        return row

# 函数 executeUpdate
# 作者：陶一丁
# 作用：数据库查找
# 最后修改时间：2019.8.22
    def executeQuery(self, sql, param=[]):
        try:
            self.connection()
            self.cls.execute(sql, param)
            result = self.cls.fetchall()
        except Exception as e:
            print(e)
        finally:
            self.free()
        return result



    # mhdb = MhDatabases()
    # result = mhdb.executeQuery("select * from test")
