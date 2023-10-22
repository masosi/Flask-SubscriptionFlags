import codecs
import os
import re
from setuptools import setup
from sys import argv

here = os.path.abspath(os.path.dirname(__file__))

try:
  README = open(os.path.join(here, 'README.md')).read()
  CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except:
  README = ''
  CHANGES = ''

install_requires = ["Flask"]

if "develop" in argv:
  install_requires.append('Sphinx')
  install_requires.append('Sphinx-PyPI-upload')


def find_version(*file_paths):
  here = os.path.abspath(os.path.dirname(__file__))
  with codecs.open(os.path.join(here, *file_paths), 'r') as f:
    version_file = f.read()
  version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                            version_file, re.M)
  if version_match:
    return version_match.group(1)
  raise RuntimeError('Unable to find version string.')


setup(
  name='Flask-SubscriptionFlags',
  version=find_version('flask_subscriptionflags', '__init__.py'),
  url='https://github.com/masosi/Flask-SubscriptionFlags',
  license='Apache',
  author='Tom Nicolosi and Rachel Sanders',
  author_email='',
  maintainer='',
  maintainer_email='',
  description='Enable or disable subscriptions in Flask apps based on configuration',
  long_description=README + '\n\n' + CHANGES,
  zip_safe=False,
  test_suite="tests",
  platforms='any',
  include_package_data=True,
  packages=[
    'flask_subscriptionflags',
    'flask_subscriptionflags.contrib',
    'flask_subscriptionflags.contrib.inline',
    'flask_subscriptionflags.contrib.sqlalchemy',
  ],
  install_requires=[
    'Flask',
    ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Python Modules'
  ]
)
