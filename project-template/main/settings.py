"""
Django settings for 'main' project.
"""

import os

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ------ Security

# Used for signing things, so keep it secret
SECRET_KEY = os.environ["SECRET_KEY"]

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
CSRF_COOKIE_SECURE = os.environ.get("SECURE_COOKIE", "true") == "true"
SESSION_COOKIE_SECURE = os.environ.get("SECURE_COOKIE", "true") == "true"
# See https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies#cookie_prefixes
SESSION_COOKIE_NAME = "__Host-sessionid"
CSRF_COOKIE_NAME = "__Host-csrftoken"

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
    "main",

    "django_tables2",
    "crispy_forms",
    "procrastinate.contrib.django",

    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",

    "main.threadlocals.ThreadLocalMiddleware",
    "main.auth.middleware.AuthenticationMiddleware",
    "main.middleware.ContentSecurityPolicyMiddleware",
    "main.middleware.NoCacheDefaultMiddleware",
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

# ------ Authentication

AUTH_USER_MODEL = "main.User"

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

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
            "formatter": "console",
        }
    },
    "filters": {"request_context": {"()": "main.logging.RequestContextFilter"}},
    "formatters": {
        "console": {
            "format": "level:levelname time:time app:app project:project channel:name request_principal:request_principal session_id_hash:session_id_hash request_id:request_id ip_address:ip_address file:pathname line:lineno message:message exception:exc_info",
            # Coopting the above string to specify the fields and ordering of the JSON
            # emitted by this class
            "class": "main.logging.JsonFormatter",
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
            "propagate": False,
        },
        "frontend": {
            "handlers": ["console"],
            "level": os.environ.get("DJANGO_LOG_LEVEL_FRONTEND", "INFO"),
            "propagate": False,
        }
    },
}

JS_REQUEST_LOG_PROB = float(os.environ.get("JS_REQUEST_LOG_PROB", "1.0"))
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

STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

# ------ App specific settings

# This is a copy of the bootstrap4 theme with a couple of small modifications
# so it still has a lot of classes in it.
CRISPY_TEMPLATE_PACK = "crispy_bedrock"
CRISPY_ALLOWED_TEMPLATE_PACKS = ("crispy_bedrock",)
