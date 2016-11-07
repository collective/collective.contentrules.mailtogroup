# -*- coding: UTF-8 -*-
from Acquisition import aq_inner
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from OFS.SimpleItem import SimpleItem
from plone.app.contentrules.browser.formhelper import AddForm
from plone.app.contentrules.browser.formhelper import EditForm
from plone.app.form.widgets.uberselectionwidget import UberMultiSelectionWidget
from plone.app.vocabularies.groups import GroupsSource
from plone.app.vocabularies.users import UsersSource
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleElementData
from plone.stringinterp.interfaces import IStringInterpolator
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from zope import schema
from zope.component import adapter
from zope.component.interfaces import ComponentLookupError
from zope.formlib import form
from zope.interface import implementer
from zope.interface import Interface


class IMailGroupAction(Interface):
    """ Definition of the configuration available for a mail action """
    subject = schema.TextLine(
        title=_(u'Subject'),
        description=_(u'Subject of the message'),
        required=True
    )

    source = schema.TextLine(
        title=_(u'Email source'),
        description=_('The email address that sends the email. If no email is \
            provided here, it will use the portal from address.'),
        required=False
    )

    members = schema.List(
        title=_(u'User(s) to mail'),
        description=_('The members where you want to send the e-mail message.'),
        value_type=schema.Choice(source=UsersSource),
        required=False
    )

    groups = schema.List(
        title=_(u'Group(s) to mail'),
        description=_('The group where you want to send this message. All \
            members of the group will receive an email.'),
        value_type=schema.Choice(source=GroupsSource),
        required=False
    )

    message = schema.Text(
        title=_(u'Message'),
        description=_(u'Type in here the message that you want to mail. Some \
            defined content can be replaced: ${title} will be replaced by the title \
            of the item. ${url} will be replaced by the URL of the item. \
            ${namedirectory} will be replaced by the Title of the folder the rule is applied to. \
            ${text} will be replace by the body-text-field (if the item has a field named \'text\') \
            and send it as HTML with a plain-text-fallback.'),
        required=True
    )


@implementer(IMailGroupAction, IRuleElementData)
class MailGroupAction(SimpleItem):
    """ The implementation of the action defined before """

    subject = u''
    source = u''
    groups = u''
    members = u''
    message = u''

    element = 'plone.actions.MailGroup'

    @property
    def summary(self):
        groups = ', '.join(self.groups)
        members = ', '.join(self.members)
        return _(u'Email report to the groups ${groups} and the members \
${members}', mapping=dict(groups=groups, members=members))


@implementer(IExecutable)
@adapter(Interface, IMailGroupAction, Interface)
class MailActionExecutor(object):
    """ The executor for this action. """

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        portal_membership = getToolByName(aq_inner(self.context), 'portal_membership')
        portal_groups = getToolByName(aq_inner(self.context), 'portal_groups')

        members = set(self.element.members)

        recipients = set()

        for groupId in self.element.groups:
            group = portal_groups.getGroupById(groupId)

            if group and group.getProperties().get('email'):
                recipients.update([group.getProperties().get('email')], )

            groupMembers = group.getGroupMemberIds()
            for memberId in groupMembers:
                members.update([memberId, ])

        for memberId in members:
            member = portal_membership.getMemberById(memberId)
            if member and member.getProperty('email'):
                recipients.update([member.getProperty('email'), ])

        mailhost = getToolByName(aq_inner(self.context), 'MailHost')
        if not mailhost:
            raise ComponentLookupError('You must have a Mailhost utility to \
execute this action')

        source = from_address = self.element.source
        urltool = getToolByName(aq_inner(self.context), 'portal_url')
        portal = urltool.getPortalObject()
        email_charset = portal.getProperty('email_charset')
        if not source:
            # no source provided, looking for the site wide from email
            # address
            from_address = portal.getProperty('email_from_address')
            if not from_address:
                raise ValueError('You must provide a source address for this \
action or enter an email in the portal properties')
            from_name = portal.getProperty('email_from_name')
            source = '%s <%s>' % (from_name, from_address)

        obj = self.event.object
        # Not all items have a text-field:
        interpolator = IStringInterpolator(obj)
        message = '\n%s' % interpolator(self.element.message)
        subject = interpolator(self.element.subject)

        # Convert set of recipients to a list:
        list_of_recipients = list(recipients)
        if not list_of_recipients:
            return False
        # Prepare multi-part-message to send html with plain-text-fallback-message,
        # for non-html-capable-mail-clients.
        # Thanks to Peter Bengtsson for valuable information about this in this post:
        # http://www.peterbe.com/plog/zope-html-emails
        mime_msg = MIMEMultipart('related')
        mime_msg['Subject'] = subject
        mime_msg['From'] = source
        # mime_msg['To'] = ""
        mime_msg['Bcc'] = ', '.join(list_of_recipients)
        mime_msg.preamble = 'This is a multi-part message in MIME format.'

        # Encapsulate the plain and HTML versions of the message body
        # in an 'alternative' part, so message agents can decide
        # which they want to display.
        msgAlternative = MIMEMultipart('alternative')
        mime_msg.attach(msgAlternative)

        # Convert html-message to plain text.
        transforms = getToolByName(aq_inner(self.context), 'portal_transforms')
        stream = transforms.convertTo('text/plain', message, mimetype='text/html')
        body_plain = stream.getData().strip()

        # We attach the plain text first, the order is mandatory.
        msg_txt = MIMEText(body_plain, _subtype='plain', _charset=email_charset)
        msgAlternative.attach(msg_txt)

        # After that, attach html.
        msg_txt = MIMEText(message, _subtype='html', _charset=email_charset)
        msgAlternative.attach(msg_txt)

        # Finally send mail.
        mailhost.send(mime_msg)

        return True


class MailGroupAddForm(AddForm):
    """ An add form for the mail action """
    form_fields = form.FormFields(IMailGroupAction)
    label = _(u'Add Mail Group Action')
    description = _(u'A mail action can mail different groups and members.')
    form_name = _(u'Configure element')
    form_fields['groups'].custom_widget = UberMultiSelectionWidget
    form_fields['members'].custom_widget = UberMultiSelectionWidget

    def create(self, data):
        a = MailGroupAction()
        form.applyChanges(a, self.form_fields, data)
        return a


class MailGroupEditForm(EditForm):
    """ An edit form for the mail action """
    form_fields = form.FormFields(IMailGroupAction)
    label = _(u'Edit Mail group Action')
    description = _(u'A mail action can mail different recipient.')
    form_name = _(u'Configure element')
    form_fields['groups'].custom_widget = UberMultiSelectionWidget
    form_fields['members'].custom_widget = UberMultiSelectionWidget
