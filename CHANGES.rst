Changelog
=========

1.6.2 (2018-06-19)
------------------

- I messed up 1.6.1 and made a brown bag release.
  [fulv]


1.6.1 (2018-06-19)
------------------

- Add note aboout unfixed regression.
  [ida]


1.6 (2016-11-08)
----------------

- Add test case for empty recipients.
  [fulv]
  
- Add support for Plone 5.0 and 5.1.  On Plone 5.x we use z3c.form instead of formlib.
  [fulv]

- Drop support for Plone 4.0, Plone 4.1 and Plone 4.2.
  Package may work, but we are no longer testing against these versions as Python 2.6 is no longer supported on code analysis.
  [hvelarde]

- Use plone.app.contentrules.ManageContentRules permission instead of cmf.ManagePortal.
  [fulv]


1.5 (2014-06-30)
-------------------

- Fixed tests and version numbering [kcleong]

- Fixed source address assignment. Now doesn't break the rule execution[cekk]

- Enabled the use of string interpolator for string substitutions [cekk]

- Add Brazilian Portuguese and Spanish translations.
  [hvelarde]

- Fix package dependencies.
  [hvelarde]



1.3.1 (2013-05-03)
-------------------

- Added help-text for text-variable. [ida]

- Added exception, if text-variable is used, but an item doesn't have a text-field.
  Concerns actions/mail.py [ida]


1.3 (2012-02-15)
-------------------

- Added fieldname 'text' as a substitutable variable and perform text-transformation,
  in order to send the message as html and as plain-text, providing a fallback
  for non-html-capable email-clients. [ida]

- Add the {namedirectory} variabel. Which can be used in the subject or message
  to show the title of the folder the rule is applied to.
  [puittenbroek]

- Add LICENSE.txt + LICENSE.GPL in /docs.
  [WouterVH]

- Remove old-style i18n-directory, and register locales-folders.
  [WouterVH]

- Add MANIFEST.in
  [WouterVH]


1.2 - 2011-04-05
----------------

- Added z3c.autoinclude in setup.py
  [kcleong]

- Using 'send' instead of deprecated 'secureSend' in Plone 4. For Plone 3
  secureSend is used.
  [kcleong]

- Use include for CMFCore in zcml, fixes permission bug in Plone 4.1
  [puittenbroek]


1.1 - 2010-12-06
----------------

- Fixed error when used on Plone 4: passing 'From' to secureSend is
  not needed in Plone 3 and breaks in Plone 4.
  [maurits]


1.0 - 2010-02-12
----------------

- No bug changes, just marking it as final.

- Must pin down plone.app.form on 1.1.8 if you're using version 1.1.8, bug
  in UberMultiSelectionWidget.
