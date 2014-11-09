import os

current_dir = os.path.dirname(os.path.abspath(__file__))
MEDIA_ROOT = os.path.join(current_dir, 'media')
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django_coverage',
    'tests',
]
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
MIDDLEWARE_CLASSES = []

AUTH_PROFILE_MODULE = 'tests.UserProfile'

# Django replaces this, but it still wants it. *shrugs*

ALLOWED_HOSTS = ['testserver']

SECRET_KEY = 'abc'
