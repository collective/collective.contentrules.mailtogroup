from setuptools import find_packages
from setuptools import setup

version = '1.5'
long_description = (
    open('README.rst').read() + '\n' +
    open('CHANGES.rst').read()
)

setup(name='collective.contentrules.mailtogroup',
      version=version,
      description="Send e-mail to groups and members defined in the action.",
      long_description=long_description,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Framework :: Plone :: 4.2',
          'Framework :: Plone :: 4.3',
          'Framework :: Plone',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='',
      author='Goldmund, Wyldebeast & Wunderliebe (K.C. Leong)',
      author_email='leong@gw20e.com',
      url='http://www.gw20e.com/',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.contentrules'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'plone.app.contentrules',
          'plone.app.form >=1.1.8'
          'plone.app.vocabularies',
          'plone.contentrules',
          'Products.CMFCore',
          'Products.CMFPlone',
          'setuptools',
          'zope.component',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.schema',
      ],
      extras_require={
          'test': [
              'Products.MailHost',
              'Products.PloneTestCase',
              'Products.SecureMailHost',
          ],
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
