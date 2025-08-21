"""
PostgreSQL database backend for Django with UTC timezone enforcement.
"""
import psycopg2

try:
    import psycopg2.extras
except ImportError as e:
    raise ImportError("Error loading psycopg2 module: %s" % e)

from django.db.backends.postgresql.base import *
from django.db.backends.postgresql.base import DatabaseWrapper as BaseDatabaseWrapper

class DatabaseWrapper(BaseDatabaseWrapper):
    def get_new_connection(self, conn_params):
        # Set timezone in connection parameters to avoid transaction issues
        conn_params['options'] = '-c timezone=UTC'
        connection = super().get_new_connection(conn_params)
        return connection
