"""
Test settings that use SQLite in-memory database for faster, isolated tests.
"""
import os
import sys
from pathlib import Path

# Add the project directory to the path so we can import settings
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from settings import *

# Override database settings for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests (optional)
class DisableMigrations:
    def __contains__(self, item):
        return True
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()