import mysql.connector
from mysql.connector import pooling, Error
from dotenv import load_dotenv
import os

load_dotenv()

_pool = None


def get_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="skillmatch_pool",
            pool_size=10,
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            database=os.getenv("DB_NAME", "skillmatch_db"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            charset="utf8mb4",
            autocommit=False,
        )
    return _pool


def get_db():
    """Return a connection from the pool."""
    return get_pool().get_connection()


def query(sql: str, params: tuple = (), fetch: str = "all"):
    """
    Execute a parameterised query safely.

    fetch:
        'all'  -> list of dicts
        'one'  -> single dict or None
        'none' -> last insert id (for INSERT/UPDATE/DELETE)
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        conn.commit()
        if fetch == "all":
            return cursor.fetchall()
        elif fetch == "one":
            return cursor.fetchone()
        else:
            return cursor.lastrowid
    except Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def execute_many(sql: str, data: list):
    """Execute a batch INSERT/UPDATE."""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.executemany(sql, data)
        conn.commit()
    except Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
