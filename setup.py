from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='collective.loremipsum',
      version=version,
      description="Creates dummy content with populated Lorem Ipsum from loripum.net",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone :: 4.1",
        "Programming Language :: Python",
        ],
      keywords='dummy data',
      author='JC Brand',
      author_email='jc@opkode.com',
      url='https://github.com/collective/collective.loremipsum',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'loremipsum',
          'Products.CMFPlone',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
