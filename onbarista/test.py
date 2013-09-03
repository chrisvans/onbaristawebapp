# Settings for running tests: test runners, in-memory database definitions, log settings

from .base import *

# TEST SETTINGS 
TEST_RUNNER = "discover_runner.DiscoverRunner"
TEST_DISCOVER_TOP_LEVEL = PROJECT_DIR
TEST_DISCOVER_ROOT = PROJECT_DIR
TEST_DISCOVER_PATTERN = "test*.py"

# Set password hasher to a much faster algorithm for tests
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

# IN-MEMORY TEST DATABASE

DATABASES = {
    "default": 
    {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
}