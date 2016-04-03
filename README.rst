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
registered using ZCML.

Usage
=====

Go to the Plone Control Panel, select Content Rules and add a new Rule.
Under 'actions' you now have a new option: Send email to groups and users.

When searching for users and groups click in the corresponding text fields, and
a pop-up menu will start showing available names.  Optionally, type the first few
letters in order to filter.

UberMultiSelectionWidget
========================
This content rule uses the Select2 widget from plone.app.widgets.

Credits
=======

Most of this package is directly copies from the plone.app.contenttules.mail
action. The package collective.contentrules.mailtolocalrole was also used as
an example.
