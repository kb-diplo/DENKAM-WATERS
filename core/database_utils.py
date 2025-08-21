"""
Database utility functions for the Water Billing System.
"""

def set_timezone_to_utc(connection, **kwargs):
    """Set the database timezone to UTC for each new connection."""
    if connection.vendor == 'postgresql':
        with connection.cursor() as cursor:
            cursor.execute("SET TIME ZONE 'UTC';")

# This function will be used in the DATABASES 'OPTIONS' setting
