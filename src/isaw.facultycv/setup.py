# -*- coding: utf-8 -*-
"""
This module contains the tool of facultycv
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.60'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('isaw', 'facultycv', 'README.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Download\n'
    '********\n')

tests_require = ['zope.testing']

setup(name='isaw.facultycv',
      version=version,
      description="FacultyCV is an educational product that allows one to create curriculum vitae for faculty members. It is along the lines of the products FacultyStaffDirectory and FacultyCV",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Topic :: Education',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
      keywords='cv resume facultycv cirriculum vitae employment university college',
      author='Christopher Warner',
      author_email='christopher.warner@nyu.edu',
      url='http://github.com/christophwarner/FacultyCV.git',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['isaw', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'xhtml2pdf',
        'Reportlab >= 2.4',
        'html5lib >= 0.90',
        'pyPdf >= 1.12',
        'collective.portlet.relateditems',
        'collective.z3cform.datagridfield',
        'plone.app.contenttypes',
      ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='isaw.facultycv.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
