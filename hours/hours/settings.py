from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "sheets",
    "livereload",
]


AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)


ACCOUNT_EMAIL_VERIFICATION = "none"
LOGIN_REDIRECT_URL = "/"
AUTH_USER_MODEL = "sheets.User"

# settings.py
APPEND_SLASH = True

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "livereload.middleware.LiveReloadScript",
]

ROOT_URLCONF = "hours.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR.joinpath("templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "hours.wsgi.application"


# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "django-file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": BASE_DIR.joinpath("error.log"),
            "formatter": "verbose",
        },
    },
    "formatters": {
        "verbose": {
            "format": ">> [%(levelname)s] %(asctime)s$ %(message)s",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["django-file"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["django-file"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}

# Password validation
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
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR.joinpath("static/")

MEDIA_URL = "hours/media/"
MEDIA_ROOT = BASE_DIR.joinpath("media/")

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

try:
    from hours.local import *
except:
    pass
