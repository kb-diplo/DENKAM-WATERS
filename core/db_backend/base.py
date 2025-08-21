"""
Custom PostgreSQL database backend that ensures UTC timezone for all connections.
"""
from django.db.backends.postgresql import base

class DatabaseWrapper(base.DatabaseWrapper):
    """
    Custom database wrapper that ensures all connections use UTC timezone.
    """
    def get_new_connection(self, conn_params):
        conn = super().get_new_connection(conn_params)
        with conn.cursor() as cursor:
            cursor.execute("SET TIME ZONE 'UTC';")
        return conn
