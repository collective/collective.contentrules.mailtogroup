#!/bin/sh

PACKAGENAME=collective.contentrules.mailtogroup   #name po-file

# use lowercase package-name for i18ndomain
I18NDOMAIN=$PACKAGENAME


# Synchronise the .pot with the templates.
i18ndude rebuild-pot --pot locales/${PACKAGENAME}.pot --create ${I18NDOMAIN} .

# Synchronise the resulting .pot with the .po files
i18ndude sync --pot locales/${PACKAGENAME}.pot locales/*/LC_MESSAGES/${PACKAGENAME}.po

# Zope3 is lazy so we have to compile the po files ourselves (Plone3.0)
# automatic compilation is fixed since plone3.1
#for lang in $(find locales -mindepth 1 -maxdepth 1 -type d); do
#    if test -d $lang/LC_MESSAGES; then
#        msgfmt -o $lang/LC_MESSAGES/${PACKAGENAME}.mo $lang/LC_MESSAGES/${PACKAGENAME}.po
#    fi
#done
