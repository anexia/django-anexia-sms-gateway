"""Settings for the test project.

Deliberately minimal: django_anexia_sms_gateway ships no models, views or URLs,
so the suite only needs an importable settings module and a test app to
discover. The ASGW_* settings the library reads are set per-test with
`override_settings`, so their `getattr` defaults stay covered here.
"""

SECRET_KEY = "test-only-not-a-secret"

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    # Test app
    "testapp",
]

MIDDLEWARE = []

ROOT_URLCONF = "core.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"
