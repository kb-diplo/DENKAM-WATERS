"""
Custom PostgreSQL database backend that ensures UTC timezone for all connections.
"""
from django.db.backends.postgresql import base

class DatabaseWrapper(base.DatabaseWrapper):
    def get_new_connection(self, conn_params):
        conn = super().get_new_connection(conn_params)
        with conn.cursor() as cursor:
            cursor.execute("SET TIME ZONE 'UTC';")
        return conn
