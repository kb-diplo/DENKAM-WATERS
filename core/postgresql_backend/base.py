"""
Custom PostgreSQL backend that ensures timezone is properly set to UTC.
"""
from django.db.backends.postgresql import base
from django.db.backends.postgresql.utils import utc_tzinfo_factory


class DatabaseWrapper(base.DatabaseWrapper):
    def init_connection_state(self):
        super().init_connection_state()
        
        # Ensure timezone is set to UTC
        with self.cursor() as cursor:
            cursor.execute("SET TIME ZONE 'UTC'")
        
        # Set the timezone factory to properly handle UTC
        self.timezone = utc_tzinfo_factory(0)
        self.timezone_name = 'UTC'
