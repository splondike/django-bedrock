"""
Django settings for 'main' project.
"""

import os

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ------ Security

# Used for signing things, so keep it secret
SECRET_KEY = os.environ.get("SECRET_KEY", "DEVKEY")

# Don't use debug mode in production
DEBUG = os.environ.get("DEBUG") == "true"

# For contexts where we need absolute URLs, this is the prefix to use
CANONICAL_URL_BASE = os.environ.get("CANONICAL_URL_BASE", "https://app.localtest.me")

if DEBUG:
    ALLOWED_HOSTS = [
        "localhost",
        ".localtest.me"
    ]
else:
    ALLOWED_HOSTS_STR = os.environ.get("ALLOWED_HOSTS", "")
    ALLOWED_HOSTS = ALLOWED_HOSTS_STR.split(";")

# Enable this if needed
# USE_X_FORWARDED_HOST = True
# Use this header to work out request IP? See main/logging.py
USE_X_FORWARDED_FOR = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_COOKIE_SECURE = os.environ.get("SECURE_COOKIE", str(not DEBUG)) == "true"
SESSION_COOKIE_SECURE = os.environ.get("SECURE_COOKIE", str(not DEBUG)) == "true"

CONTENT_SECURITY_POLICY_ACTIVE = os.environ.get(
    "CONTENT_SECURITY_POLICY_ACTIVE",
    "active"
)
CONTENT_SECURITY_POLICY_REPORT_PROB = float(os.environ.get(
    "CONTENT_SECURITY_POLICY_ACTIVE",
    "1.0"
))

# ------ Application definition

INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "main"
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",

    "main.threadlocals.ThreadLocalMiddleware",
    "main.middleware.ContentSecurityPolicyMiddleware",
    "main.middleware.SlowPageLogMiddleware",
    "main.middleware.NoCacheDefaultMiddleware",

    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "main.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "main.context_processors.debug",
                "main.context_processors.frontend_logging",
            ],
        },
    },
]

WSGI_APPLICATION = "main.wsgi.application"


# ------ Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("DB_HOST", "database"),
        "NAME": os.environ.get("DB_NAME", "postgres"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "password"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ------ Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-au"

TIME_ZONE = "Australia/Melbourne"

USE_I18N = True

USE_TZ = True

# ------ Logging

# See
# https://docs.python.org/3/library/logging.config.html#logging-config-dictschema
# for config details
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "filters": ["request_context"],
            "formatter": "console"
        }
    },
    "filters": {
        "request_context": {
            "()": "main.logging.RequestContextFilter"
        }
    },
    "formatters": {
        "console": {
            "format": (
                "{asctime} {ip_token} {session_token} {trace_id} "
                "[{name}] {levelname} {message}"
            ),
            "style": "{"
        }
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("DJANGO_LOG_LEVEL", "WARNING"),
    },
    "loggers": {
        "security": {
            # Include all security messages even if they're just INFO
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        }
    }
}

SLOW_REQUEST_THRESHOLD_MS = int(
    os.environ.get("SLOW_REQUEST_THRESHOLD_MS", "500")
)

JS_ERROR_LOG_PROB = float(os.environ.get("JS_ERROR_LOG_PROB", "1.0"))

# ------ Email

DEFAULT_FROM_EMAIL = SERVER_EMAIL = "noreply@example.com"
# Don't spam superusers with any errors
ADMINS = ()

if os.environ.get("EMAIL_HOST"):
    EMAIL_HOST = os.environ.get("EMAIL_HOST")
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "25"))
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
    # EMAIL_USE_TLS/EMAIL_USE_SSL

# ------ Static files (CSS, JavaScript, Images)

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ------ App specific settings
