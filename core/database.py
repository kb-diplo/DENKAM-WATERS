from django.db.backends.postgresql.base import DatabaseWrapper as OriginalDatabaseWrapper
from django.db.backends.postgresql.operations import DatabaseOperations as OriginalDatabaseOperations

class DatabaseOperations(OriginalDatabaseOperations):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set timezone to UTC for all connections
        self.connection_init_sql = "SET TIME ZONE 'UTC';"

class DatabaseWrapper(OriginalDatabaseWrapper):
    def get_new_connection(self, conn_params):
        conn = super().get_new_connection(conn_params)
        # Ensure timezone is set to UTC
        with conn.cursor() as cursor:
            cursor.execute("SET TIME ZONE 'UTC';")
        return conn
