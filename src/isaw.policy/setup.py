from setuptools import setup, find_packages
import os

version = '1.0-dev'

long_description = (
    open('README.rst').read()
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')

setup(name='isaw.policy',
      version=version,
      description="Policy product for the Institute for Study of the Ancient World",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
        "Framework :: Zope2",
        "Framework :: Plone",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='Plone, policy, isaw',
      author='Jazkarta, Inc.',
      author_email='cris@crisewing.com',
      url='https://github.com/isawnyu/isaw.policy/',
      license='gpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['isaw', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          #'isaw.facultycv',
          'isaw.theme',
          'isaw.exhibitions',
          #'isaw.bibitems',
          'plone.app.caching',
          'collective.linkcheck',
          'collective.progressbar',
          'collective.portlet.relateditems',
          'plone.api',
          'Products.CMFPlacefulWorkflow',
          'Products.WebServerAuth',
          'randomdotorg',
          'tweepy',
          'z3c.jbot',
          'collective.embedly',
          'plone.app.imagecropping',
          'Products.PloneKeywordManager',
          'collective.easyslider',
          'collective.easytemplate',
          'Products.RedirectionTool',
          #'plone.formwidget.geolocation',
          'plone.app.iterate',
          'plone.app.textfield',
          #'collective.z3cform.datagridfield',
      ],
      extras_require={'test': ['plone.app.testing']},
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """
      )
