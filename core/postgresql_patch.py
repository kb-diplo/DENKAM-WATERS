"""
Patch for Django's PostgreSQL backend to handle timezone issues.
"""
from django.db.backends.postgresql import base
from django.db.backends.postgresql.utils import utc_tzinfo_factory as original_utc_tzinfo_factory

def patched_utc_tzinfo_factory(offset):
    """Patched version of utc_tzinfo_factory that doesn't enforce UTC."""
    from django.utils.timezone import utc
    return utc

# Apply the patch
import django.db.backends.postgresql.utils
django.db.backends.postgresql.utils.utc_tzinfo_factory = patched_utc_tzinfo_factory

# Also patch the base module's utc_tzinfo_factory reference
base.utc_tzinfo_factory = patched_utc_tzinfo_factory
