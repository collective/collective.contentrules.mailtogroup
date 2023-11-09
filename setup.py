from setuptools import find_packages
from setuptools import setup


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
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    keywords="plone automatic content rules",
    author="Goldmund, Wyldebeast & Wunderliebe (K.C. Leong)",
    author_email="leong@gw20e.com",
    url="https://github.com/collective/collective.contentrules.mailtogroup",
    license="GPL version 2",
    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=["collective", "collective.contentrules"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "Products.CMFPlone",
        "plone.app.dexterity",
        "plone.app.contentrules",
        "plone.contentrules",
        "Products.CMFCore",
        "setuptools",
        "zope.component",
        "zope.i18nmessageid",
        "zope.interface",
        "zope.schema",
        "Products.statusmessages",
        "plone.app.z3cform",
        "plone.autoform",
        "plone.registry",
        "plone.stringinterp",
    ],
    extras_require={
        "test": [
            "plone.api",
            "plone.base",
            "plone.restapi",
            "plone.browserlayer",
            "plone.app.dexterity",
            "plone.app.testing",
            "plone.testing>=5.0.0",
            "plone.app.robotframework[debug]",
        ],
    },
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
