from setuptools import find_packages, setup


version = "2.0.0.dev0"
long_description = open("README.rst").read() + "\n" + open("CHANGES.rst").read()

setup(
    name="collective.contentrules.mailtogroup",
    version=version,
    description="Send e-mail to groups and members defined in the action.",
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="plone automatic content rules",
    author="Goldmund, Wyldebeast & Wunderliebe (K.C. Leong)",
    author_email="leong@gw20e.com",
    url="https://github.com/collective/collective.contentrules.mailtogroup",
    packages=find_packages(exclude=["ez_setup"]),
    namespace_packages=["collective", "collective.contentrules"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "plone.app.contentrules",
        "plone.app.form >=1.1.8",
        "plone.app.vocabularies",
        "plone.api",
        "plone.contentrules",
        "Products.CMFCore",
        "Products.CMFPlone",
        "setuptools",
        "zope.component",
        "zope.i18nmessageid",
        "zope.interface",
        "zope.schema",
    ],
    extras_require={
        "test": [
            "plone.app.robotframework",
            "plone.app.testing [robot]",
            "Products.MailHost",
            "Products.SecureMailHost",
            "robotsuite",
        ],
    },
    entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
