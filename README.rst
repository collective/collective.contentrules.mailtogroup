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

The variable `${namedirectory}` for an item's parent-folder-name, and the
variable `${text}` for an item's body-text-field, won't be substituted anymore
since of version 1.5, due to an unintentional breaking commit introducing the
regressions whicht haven't been restored since then.

If you want to use these variables, you need to pin this add-on to the
preceding version, see installation-section below.


Installation
============

In your buildout-config, add collective.contentrules.mailtogroup to the 
egg- and zcml-section in the [instance]-part:

    [buildout]
    parts =
        instance

    [instance]
    recipe = plone.recipe.zope2instance

    eggs =
        Plone
        collective.contentrules.mailtogroup

    zcml =
        collective.contentrules.mailtogroup


To define a specific version (see "Disclaimer" above), additionally add a
[versions]-part, if not existing already, and pin the wanted version:

    [buildout]
    versions = versions

    [versions]
    collective.contentrules.mailtogroup = 1.3.1


After altering the buildout-config, you need to run buildout and restart
the server:

    $ cd yourPloneServerDirectory
    $ ./bin/buildout
    $ ./bin/instance restart # For ZEO-setups do this with all the clients.


An activation of this add-on via a Plone-site's controlpanel is not necessary,
the features of this add-on will be immediately available to all Plone-sites of
the ZOPE-instance.


Usage
=====

Go to the Plone Control Panel, select Content Rules and add a new Rule.
Under 'actions' you now have a new option: Send email to groups and users.

When searching for users and groups make sure you press the search button. Don't
hit enter. Search results for these items are only shown when you press search.


Credits
=======

Most of this package is directly copies from the plone.app.contenttules.mail
action. The package collective.contentrules.mailtolocalrole was also used as
an example.
