import pymysql
from pymysql.cursors import DictCursor
from ncatbot.utils import logger
import yaml

_log = logger.get_log()

def get_KTPdb(config_path:str):
    with open(config_path) as f:
        database_config = yaml.load(f, Loader=yaml.FullLoader)
    db_config = {
        'host': database_config['host'],
        'user': database_config['user'],
        'password': database_config['password'],
        'database': database_config['database']
    }
    return KTPDatabase(**db_config)

class KTPDatabase:
    def __init__(self, host, user, password, database):
        """初始化数据库连接"""
        self.connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=DictCursor
        )
        _log.info("数据库连接成功")

    def __del__(self):
        """析构函数，关闭数据库连接"""
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
            _log.info("数据库连接已关闭")

    def create_user(self, user_id, ktp_username=None, ktp_password=None, token=None):
        """创建新用户"""
        try:
            with self.connection.cursor() as cursor:
                sql = """
                INSERT INTO tb_ktp (user_id, ktp_username, ktp_password, token)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (user_id, ktp_username, ktp_password, token))
            self.connection.commit()
            _log.info(f"用户 {user_id} 创建成功")
            return True
        except pymysql.Error as e:
            _log.error(f"创建用户失败: {e}")
            return False

    def read_user(self, user_id):
        """读取用户信息"""
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT * FROM tb_ktp WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()
                if result:
                    _log.info(f"用户 {user_id} 信息: {result}")
                else:
                    _log.warning(f"未找到用户 {user_id}")
                return result
        except pymysql.Error as e:
            _log.error(f"读取用户失败: {e}")
            return None

    def update_user(self, user_id, ktp_username=None, ktp_password=None, token=None):
        """更新用户信息"""
        try:
            with self.connection.cursor() as cursor:
                # 构建动态更新的SQL语句
                updates = []
                params = []
                if ktp_username is not None:
                    updates.append("ktp_username = %s")
                    params.append(ktp_username)
                if ktp_password is not None:
                    updates.append("ktp_password = %s")
                    params.append(ktp_password)
                if token is not None:
                    updates.append("token = %s")
                    params.append(token)

                if not updates:
                    _log.info("没有提供更新字段")
                    return False

                sql = f"UPDATE tb_ktp SET {', '.join(updates)} WHERE user_id = %s"
                params.append(user_id)
                cursor.execute(sql, tuple(params))
                affected_rows = cursor.rowcount
                self.connection.commit()

                if affected_rows > 0:
                    _log.info(f"用户 {user_id} 更新成功")
                else:
                    _log.info(f"未找到用户 {user_id} 或无需更新")
                return affected_rows > 0
        except pymysql.Error as e:
            _log.error(f"更新用户失败: {e}")
            return False

    def delete_user(self, user_id):
        """删除用户"""
        try:
            with self.connection.cursor() as cursor:
                sql = "DELETE FROM tb_ktp WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                affected_rows = cursor.rowcount
                self.connection.commit()

                if affected_rows > 0:
                    _log.info(f"用户 {user_id} 删除成功")
                else:
                    _log.info(f"未找到用户 {user_id}")
                return affected_rows > 0
        except pymysql.Error as e:
            _log.error(f"删除用户失败: {e}")
            return False

    def list_all_users(self):
        """列出所有用户"""
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT user_id, ktp_username FROM tb_ktp"
                cursor.execute(sql)
                results = cursor.fetchall()
                _log.info(f"共找到 {len(results)} 个用户")
                return results
        except pymysql.Error as e:
            _log.error(f"获取用户列表失败: {e}")
            return []


# 示例用法
if __name__ == "__main__":

    # 创建数据库操作实例
    ktp_db = get_KTPdb('../../database_config.yaml')

    # 测试CRUD操作
    test_user_id = '1319507316'

    res = ktp_db.read_user(test_user_id)['user_id']
    print(res)