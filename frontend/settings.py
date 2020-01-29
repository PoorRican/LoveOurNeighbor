"""
Django settings for frontend project.

Generated by 'django-admin startproject' using Django 2.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from django.urls import reverse_lazy


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qh*ctnmwh9xbzjtndzgaqm3x)3zmkxzlpa!411xvm0xdl99d+g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.environ.get('DEBUG', 0)))

ASSETS_DEBUG = True

# Verification Feature Switches
REQUIRE_MINISTRY_VERIFICATION = False  # TODO: implement
REQUIRE_USER_VERIFICATION = False

# Feature Switches
COMMENTS = False

ALLOWED_HOSTS = ["localhost", "dev.loveourneighbor.org", "loveourneighbor.org", "demo.loveourneighbor.org",
                 "repo.loveourneighbor.org", "www.loveourneighbor.org"]


# Application definition

INSTALLED_APPS = [
    'public.apps.PublicConfig',

    'ministry.apps.MinistryConfig',
    'campaign.apps.CampaignConfig',
    'news.apps.NewsConfig',

    'tag.apps.TagConfig',
    'comment.apps.CommentConfig',
    'people.apps.PeopleConfig',
    'donation.apps.DonationConfig',
    'explore.apps.ExploreConfig',

    'django_assets',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'frontend.utils.TimezoneMiddleware'
]

ROOT_URLCONF = 'frontend.urls'

TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.filesystem.Loader',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ]
        }
    },
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': ['templates/',

                 'templates/macros/',
                 'templates/macros/parts',
                 'templates/macros/layout',

                 'templates/ministry/',
                 'templates/campaign/',
                 'templates/news/',

                 'templates/donation/',
                 'templates/people/',
                 'templates/public/',
                 ],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'frontend.jinja.environment'
        },
    }
]

WSGI_APPLICATION = 'frontend.wsgi.application'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("SQL_DATABASE", os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": os.environ.get("SQL_USER", "user"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
        "HOST": os.environ.get("SQL_HOST", "localhost"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
          'min_length': 9,
         }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher'
]

AUTH_USER_MODEL = 'people.User'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = reverse_lazy('people:login')

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False  # temporarily disabled for a performance boost

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "django_assets.finders.AssetsFinder"
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# bundled assets config
ASSETS_MODULES = [
    'frontend.assets'
]

if DEBUG:
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, '/static/')

    # just place media files in 'static' directory while debugging
    MEDIA_ROOT = os.path.join(BASE_DIR, 'static/media/')
    MEDIA_URL = '/media/'

    ASSETS_URL = '/static/'
    ASSETS_AUTO_BUILD = True

else:
    STATIC_URL = '/staticfiles/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

    MEDIA_URL = '/mediafiles/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

    ASSETS_URL = STATIC_URL
    ASSETS_AUTO_BUILD = False

# Google Analytics
GA_TRACKING_ID = 'UA-153638464-1'

# PAYEEZY
PAYEEZY_TEST_BUTTON = DEBUG  # determines if jinja template uses test network or not

# Mailgun Values
MG_DOMAIN = 'mg.loveourneighbor.org'
MG_API_KEY = 'f64271df50355a0fc10236b82e439ad1-af6c0cec-56113993'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django_debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

DEFAULT_PROFILE_IMG = 'img/blank_profile.jpg'
