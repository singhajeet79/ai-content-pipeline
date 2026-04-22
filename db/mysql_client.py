import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv


# 🔴 LOAD ENV VARIABLES
load_dotenv()


class MySQLClient:
    """
    MySQL Client Wrapper

    - Single connection per process
    - Fail-fast connection validation
    - Env-driven config (NO hardcoded secrets)
    """

    _connection = None

    def __init__(self):
        self.host = os.getenv("MYSQL_HOST", "localhost")
        self.port = int(os.getenv("MYSQL_PORT", 3306))
        self.user = os.getenv("MYSQL_USER")
        self.password = os.getenv("MYSQL_PASSWORD")
        self.database = os.getenv("MYSQL_DB")

        # 🔴 HARD FAIL if missing config
        if not all([self.user, self.password, self.database]):
            raise RuntimeError(
                "❌ Missing MySQL configuration. "
                "Set MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB in .env"
            )

        if MySQLClient._connection is None:
            try:
                MySQLClient._connection = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )

                if not MySQLClient._connection.is_connected():
                    raise RuntimeError("MySQL connection failed")

                print("✅ MySQL Connected")

            except Error as e:
                raise RuntimeError(f"❌ MySQL connection failed: {e}")

        self.conn = MySQLClient._connection

    def get_cursor(self):
        return self.conn.cursor(dictionary=True)

    def commit(self):
        self.conn.commit()