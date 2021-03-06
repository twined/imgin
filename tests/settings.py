import os

current_dir = os.path.dirname(os.path.abspath(__file__))
imgin_dir = os.path.dirname(os.path.abspath(os.path.join(current_dir,
                                                         '..', 'imgin')))

TEMPLATE_DIRS = [
    os.path.join(imgin_dir, 'imgin', 'templates').replace(' ', r'\ '),
]

MEDIA_ROOT = os.path.join(current_dir, 'media')
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django_coverage',
    'django_nose',
    'cerebrum',
    'crispy_forms',
    'tests',
]

STATIC_URL = '/static/'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--with-progressive', '--logging-clear-handlers']

COVERAGE_REPORT_HTML_OUTPUT_DIR = os.path.join(current_dir, 'coverage_report')
COVERAGE_CUSTOM_REPORTS = False
COVERAGE_MODULE_EXCLUDES = ['tests$', 'settings$', 'urls$', 'locale$',
                            'common.views.test', '__init__', 'django',
                            'migrations']

ROOT_URLCONF = 'tests.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
        'OPTIONS': {
            'DB': 1,
            'PARSER_CLASS': 'redis.connection.HiredisParser',
        },
        'KEY_PREFIX': 'imgin',
    },
}

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 1,
        'DEFAULT_TIMEOUT': 360,
    }
}

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'tests.tests.TestcaseUserBackend',
]

#LOGIN_URL = '/admin/login/'
#LOGOUT_URL = '/admin/logout/'

CRISPY_TEMPLATE_PACK = 'bootstrap3'

AUTH_PROFILE_MODULE = 'tests.UserProfile'

# Django replaces this, but it still wants it. *shrugs*

ALLOWED_HOSTS = ['testserver']

SECRET_KEY = 'abc'
