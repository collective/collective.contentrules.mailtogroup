.. image:: https://secure.travis-ci.org/collective/collective.contentrules.mailtogroup.png?branch=master
    :target: http://travis-ci.org/collective/collective.contentrules.mailtogroup
    :alt: Travis CI badge

.. image:: https://coveralls.io/repos/collective/collective.contentrules.mailtogroup/badge.png?branch=master
    :target: https://coveralls.io/r/collective/collective.contentrules.mailtogroup
    :alt: Coveralls badge

.. image:: https://pypip.in/d/collective.contentrules.mailtogroup/badge.png
    :target: https://pypi.python.org/pypi/collective.contentrules.mailtogroup/
    :alt: Downloads

Introduction
============

This action rule allows you to send e-mail to groups and users. The groups and
users are defined in the action rule, it's possible to combine both. This action
was made because the current actions cannot mail to a dynamic set of users (group).
Adding multiple members was also added because you don't always know the e-mail of
a certain user.

Installation
============

Add collective.contentrules.mailtogroup to your buildout as an egg or
from source. No (generic setup) installation is necessary, the action is 
registered using ZCML. So do add the package to the zcml slug list of your
[instance] section.

Usage
=====

Go to the Plone Control Panel, select Content Rules and add a new Rule. 
Under 'actions' you now have a new option: Send email to groups and users.

When searching for users and groups make sure you press the search button. Don't
hit enter. Search results for these items are only shown when you press search.

UberMultiSelectionWidget
========================
This content rule uses the UberMultiSelectionWidget from plone.app.form. This 
widget is broken in version 1.1.7 of plone.app.form. Plone 3.3.4 has this version.

As of version 1.1.8 the widget is working again. To use the correct version pin 
down plone.app.form:

[versions]
...
plone.app.form = 1.1.8

Credits
=======

Most of this package is directly copies from the plone.app.contenttules.mail
action. The package collective.contentrules.mailtolocalrole was also used as 
an example.
