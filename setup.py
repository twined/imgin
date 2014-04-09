# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='imgin',
    version='0.3.3',
    author=u'Twined',
    author_email='www.twined.net',
    packages=find_packages(),
    include_package_data=True,
    url='http://github.com/twined/imgin',
    license='Do what thou wilt.',
    description='Image manipulation for twined apps',
    long_description=open('README.md').read(),
    zip_safe=False,
)
