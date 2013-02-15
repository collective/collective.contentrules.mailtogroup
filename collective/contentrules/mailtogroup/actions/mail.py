from Acquisition import aq_inner
from OFS.SimpleItem import SimpleItem
from zope.component import adapts
from zope.component.interfaces import ComponentLookupError
from zope.interface import Interface, implements
from zope.formlib import form
from zope import schema

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 
from plone.app.vocabularies.groups import GroupsSource
from plone.app.vocabularies.users import UsersSource
from plone.app.form.widgets.uberselectionwidget import UberMultiSelectionWidget
from plone.contentrules.rule.interfaces import IRuleElementData, IExecutable

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import safe_unicode


class IMailGroupAction(Interface):
    """Definition of the configuration available for a mail action
    """
    subject = schema.TextLine(title=_(u"Subject"),
                              description=_(u"Subject of the message"),
                              required=True)
    source = schema.TextLine(title=_(u"Email source"),
                             description=_("The email address that sends the \
email. If no email is provided here, it will use the portal from address."),
                             required=False)
    members = schema.List(title=_(u"User(s) to mail"),
                        description=_("The members where you want to\
 send the e-mail message."),
                        value_type=schema.Choice(source=UsersSource),
                        required=False)
    groups = schema.List(title=_(u"Group(s) to mail"),
                         description=_("The group where you want to\
 send this message. All members of the group will receive an email."),
                         value_type=schema.Choice(source=GroupsSource),
                         required=False)
    message = schema.Text(title=_(u"Message"),
                          description=_(u"Type in here the message that you \
want to mail. Some defined content can be replaced: ${title} will be replaced \
by the title of the item. ${url} will be replaced by the URL of the item."),
                          required=True)

class MailGroupAction(SimpleItem):
    """
    The implementation of the action defined before
    """
    implements(IMailGroupAction, IRuleElementData)

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
        return _(u"Email report to the groups ${groups} and the members \
${members}", mapping=dict(groups=groups, members=members))


class MailActionExecutor(object):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, IMailGroupAction, Interface)

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
                recipients.update([group.getProperties().get('email')],)

            groupMembers = group.getGroupMemberIds()
            for memberId in groupMembers:
                members.update([memberId,])
 
        for memberId in members:
            member = portal_membership.getMemberById(memberId)
            if member and member.getProperty('email'):
               recipients.update([member.getProperty('email'),])
            
        mailhost = getToolByName(aq_inner(self.context), "MailHost")
        if not mailhost:
            raise ComponentLookupError, 'You must have a Mailhost utility to \
execute this action'

        source = self.element.source
        urltool = getToolByName(aq_inner(self.context), "portal_url")
        portal = urltool.getPortalObject()
        email_charset = portal.getProperty('email_charset')
        if not source:
            # no source provided, looking for the site wide from email
            # address
            from_address = portal.getProperty('email_from_address')
            if not from_address:
                raise ValueError, 'You must provide a source address for this \
action or enter an email in the portal properties'
            from_name = portal.getProperty('email_from_name')
            source = "%s <%s>" % (from_name, from_address)

        obj = self.event.object
        event_title = safe_unicode(obj.Title())
        event_url = obj.absolute_url()
        message = self.element.message.replace("${url}", event_url)
        message = message.replace("${title}", event_title)

        subject = self.element.subject.replace("${url}", event_url)
        subject = subject.replace("${title}", event_title)

        for email_recipient in recipients:
            self.context.plone_log('sending to: %s' % email_recipient)

            try: # sending mail in Plone 4
                mailhost.send(message, mto=email_recipient, mfrom=source,
                        subject=subject, charset=email_charset)
            except: #sending mail in Plone 3
                mailhost.secureSend(message, email_recipient, source,
                        subject=subject, subtype='plain',
                        charset=email_charset, debug=False)


        return True

class MailGroupAddForm(AddForm):
    """
    An add form for the mail action
    """
    form_fields = form.FormFields(IMailGroupAction)
    label = _(u"Add Mail Group Action")
    description = _(u"A mail action can mail different groups and members.")
    form_name = _(u"Configure element")
    form_fields['groups'].custom_widget = UberMultiSelectionWidget
    form_fields['members'].custom_widget = UberMultiSelectionWidget



    def create(self, data):
        a = MailGroupAction()
        form.applyChanges(a, self.form_fields, data)
        return a

class MailGroupEditForm(EditForm):
    """
    An edit form for the mail action
    """
    form_fields = form.FormFields(IMailGroupAction)
    label = _(u"Edit Mail group Action")
    description = _(u"A mail action can mail different recipient.")
    form_name = _(u"Configure element")
    form_fields['groups'].custom_widget = UberMultiSelectionWidget
    form_fields['members'].custom_widget = UberMultiSelectionWidget
