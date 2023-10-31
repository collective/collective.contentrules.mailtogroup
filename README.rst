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


Disclaimer
==========

The variable `${namedirectory}` for an item's parent folder name, and the
variable `${text}` for an item's body text field, won't be substituted anymore
since version 1.5, due to an unintentional breaking commit introducing the
regressions which haven't been restored since then.

If you want to use these variables, you need to pin this add-on to the
preceding version (`1.3.1`_), see installation section below.

.. _1.3.1: https://pypi.org/project/collective.contentrules.mailtogroup/1.3.1/


Installation
============

Please refer to Plone's official documentation for `installing add-ons`_
and `pinning specific add-on versions`_.

An activation of this add-on via a Plone site's controlpanel is not necessary,
the features of this add-on will be immediately available to all Plone sites of
the ZOPE instance.

.. _installing add-ons: https://docs.plone.org/manage/installing/installing_addons.html#installing-add-ons-using-buildout
.. _pinning specific add-on versions: https://docs.plone.org/manage/installing/installing_addons.html#pinning-add-on-versions


Usage
=====

Go to the Plone Control Panel, select Content Rules and add a new Rule.
Under 'actions' you now have a new option: Send email to groups and users.

When searching for users and groups make sure you press the search button. Don't
hit enter. Search results for these items are only shown when you press search.


Future
======

This add-on has been `approved`_ for inclusion in the core of Plone.
When that happens, independent development of it might cease.

.. _approved: https://github.com/plone/Products.CMFPlone/issues/1808


Credits
=======

Most of this package is directly copied from the plone.app.contenttules.mail
action. The package collective.contentrules.mailtolocalrole was also used as
an example.

