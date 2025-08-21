"""
Database router that ensures all database connections use UTC timezone.
"""
from django.db import connections

class TimezoneRouter:
    """
    Database router that ensures all database connections use UTC timezone.
    """
    def db_for_read(self, model, **hints):
        self._set_timezone()
        return None

    def db_for_write(self, model, **hints):
        self._set_timezone()
        return None

    def _set_timezone(self):
        """Set the timezone to UTC for the default database connection."""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SET TIME ZONE 'UTC';")

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return None
