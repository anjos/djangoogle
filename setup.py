#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Created by Andre Anjos <andre.dos.anjos@cern.ch>
# Seg 14 Set 2009 14:42:06 CEST

"""Installation instructions for djangoogle
"""

from setuptools import setup, find_packages

setup(

    name = "djangoogle",
    version = "0.5.4",
    packages = find_packages(),

    # we also need all translation files and templates
    package_data = {
      'djangoogle': [
        'templates/djangoogle/*.html',
        'templates/djangoogle/embed/*.html',
        'media/css/*.css',
        'media/img/svg/*',
        'media/img/png/readme.txt',
        'media/img/png/*/*.png',
        'locale/*/LC_MESSAGES/django.po',
        'locale/*/LC_MESSAGES/django.mo',
        ],
      },

    zip_safe=False,

    install_requires = [
      'gdata>=2.0.0',
      'Django>=1.1',
      'docutils',
      'pytz',
      'pillow',
      ],

    dependency_links = [
      'http://docutils.sourceforge.net/docutils-snapshot.tgz',
      'http://www.pythonware.com/products/pil/',
      ],

    # metadata for upload to PyPI
    author = "Andre Anjos",
    author_email = "andre.dos.anjos@gmail.com",
    description = "Provides integration between Django and Google applications",
    license = "PSF",
    keywords = "gdata django google calendar youtube picasaweb",
    url = "",   # project home page, if any

)

