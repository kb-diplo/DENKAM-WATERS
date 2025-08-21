"""
Core application initialization.
"""
# PostgreSQL patches not needed for MySQL deployment
# try:
#     from .postgresql_patch import patched_utc_tzinfo_factory
#     import django.db.backends.postgresql.utils
#     django.db.backends.postgresql.utils.utc_tzinfo_factory = patched_utc_tzinfo_factory
#     
#     # Also patch the base module's reference
#     from django.db.backends.postgresql import base
#     base.utc_tzinfo_factory = patched_utc_tzinfo_factory
# except ImportError:
#     pass

# Use PyMySQL as MySQL driver if mysqlclient is not available
try:
    import MySQLdb
except ImportError:
    import pymysql
    pymysql.install_as_MySQLdb()
