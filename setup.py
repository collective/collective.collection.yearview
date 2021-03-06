from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='collective.collection.yearview',
      version=version,
      description="Plone Topic view which allows visitors to filter summary listing by chosen year",
      long_description=open("README.rst").read() + "\n" + 
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone collection year timeline',
      author='Mikko Ohtamaa',
      author_email='mikko.ohtamaa@twinapex.fi',
      url='http://www.twinapex.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.collection'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Plone',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
