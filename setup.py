# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='imgin',
    version='1.0.1',
    author=u'Twined',
    author_email='www.twined.net',
    packages=find_packages(),
    include_package_data=True,
    url='http://github.com/twined/imgin',
    license='Do what thou wilt.',
    description='Image manipulation for Twined apps',
    long_description=open('README.md').read(),
    install_requires=[
        "mock-django",
        "nose",
        "Django==1.7.1",
        "Pillow==2.6.0",
        "django_rq==0.7.0",
        "django-redis-cache==0.13.0",
        "django-crispy-forms==1.4.0",
    ],
    dependency_links=[
        'https://github.com/twined/cerebrum/tarball/master#egg=cerebrum-dev',
    ],
    zip_safe=False,
)
