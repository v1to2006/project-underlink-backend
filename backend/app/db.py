import os
from contextlib import contextmanager

import pymysql
from pymysql.cursors import DictCursor


def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "game_user"),
        password=os.getenv("DB_PASSWORD", "game_password"),
        database=os.getenv("DB_NAME", "deep_drift"),
        cursorclass=DictCursor,
        autocommit=False,
    )


@contextmanager
def get_cursor():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            yield connection, cursor
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()