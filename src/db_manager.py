import psycopg2
from psycopg2.extras import execute_batch
from contextlib import contextmanager
import os

class DBManager:
    def __init__(self, db_config):
        self.db_config = db_config

    @contextmanager
    def connect(self):
        conn = psycopg2.connect(**self.db_config)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def execute(self, query, params=None):
        with self.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    def execute_many(self, query, params=None):
        with self.connect() as conn:
            with conn.cursor() as cursor:
                execute_batch(cursor, query, params)