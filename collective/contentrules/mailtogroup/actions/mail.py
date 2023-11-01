from Acquisition import aq_inner
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from OFS.SimpleItem import SimpleItem
from plone.app.contentrules.actions import ActionAddForm, ActionEditForm
from plone.app.contentrules.browser.formhelper import ContentRuleFormWrapper
from plone.app.z3cform.widget import SelectWidget
from plone.autoform import directives
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from plone.registry.interfaces import IRegistry
from plone.stringinterp.interfaces import IStringInterpolator
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IMailSchema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope import schema
from zope.component import adapter, getUtility
from zope.interface.interfaces import ComponentLookupError
#from zope.component.interfaces import ComponentLookupError
from zope.globalrequest import getRequest
from zope.interface import implementer, Interface
from plone import api

import logging


logger = logging.getLogger(__file__)


class IMailGroupAction(Interface):
    """Definition of the configuration available for a mail action"""

    subject = schema.TextLine(
        title=_("Subject"),
        description=_("Subject of the message"),
        required=True,
    )

    source = schema.TextLine(
        title=_("Email source"),
        description=_(
            "The email address that sends the email. If no email is \
            provided here, it will use the portal from address."
        ),
        required=False,
    )

    directives.widget("members", SelectWidget)
    members = schema.List(
        title=_("User(s) to mail"),
        description=_("The members where you want to send the e-mail message."),
        value_type=schema.Choice(vocabulary="plone.app.vocabularies.Users"),
        required=False,
    )

    directives.widget("groups", SelectWidget)
    groups = schema.List(
        title=_("Group(s) to mail"),
        description=_(
            "The group where you want to send this message. All \
            members of the group will receive an email."
        ),
        value_type=schema.Choice(vocabulary="plone.app.vocabularies.Groups"),
        required=False,
    )

    message = schema.Text(
        title=_("Message"),
        description=_(
            "Type in here the message that you want to mail. Some \
            defined content can be replaced: ${title} will be replaced by the title \
            of the item. ${url} will be replaced by the URL of the item. \
            ${namedirectory} will be replaced by the Title of the folder the rule is applied to. \
            ${text} will be replace by the body-text-field (if the item has a field named 'text') \
            and send it as HTML with a plain-text-fallback."
        ),
        required=True,
    )


@implementer(IMailGroupAction, IRuleElementData)
class MailGroupAction(SimpleItem):
    """The implementation of the action defined before"""

    subject = ""
    source = ""
    groups = ""
    members = ""
    message = ""

    element = "plone.actions.MailGroup"
    

    @property
    def summary(self):
        groups = self.groups and "the groups " + ", ".join(self.groups) or ""
        members = self.members and "the members " + ", ".join(self.members) or ""
        both = (groups and members) and " and " or ""
        return _(
            "Email report to ${groups} ${both} ${members}",
            mapping=dict(groups=groups, both=both, members=members),
        )


@implementer(IExecutable)
@adapter(Interface, IMailGroupAction, Interface)
class MailActionExecutor:
    """The executor for this action."""

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event
        registry = getUtility(IRegistry)
        self.mail_settings = registry.forInterface(IMailSchema, prefix="plone")

    def __call__(self):
        mailhost = getToolByName(aq_inner(self.context), "MailHost")
        if not mailhost:
            abc = 1
            raise ComponentLookupError(
                "You must have a Mailhost utility to \
            execute this action"
            )

        self.email_charset = self.mail_settings.email_charset

        obj = self.event.object

        interpolator = IStringInterpolator(obj)

        self.source = self.element.source
        if self.source:
            self.source = interpolator(self.source).strip()

        if not self.source:
            # no source provided, looking for the site wide from email
            # address
            from_address = self.mail_settings.email_from_address
            if not from_address:
                # the mail can't be sent. Try to inform the user
                request = getRequest()
                if request:
                    messages = IStatusMessage(request)
                    msg = _(
                        "Error sending email from content rule. You must "
                        "provide a source address for mail "
                        "actions or enter an email in the portal properties"
                    )
                    messages.add(msg, type="error")
                return False
            from_name = self.mail_settings.email_from_name.strip('"')
            self.source = f"{from_name} <{from_address}>"
            
        
        
        self.recipients = ", ".join(self.get_recipients())
        
        # prepend interpolated message with \n to avoid interpretation
        # of first line as header
        message = f"\n{interpolator(self.element.message)!s}"
        # self.subject = interpolator(self.element.subject)
        
        outer = MIMEMultipart('alternative')
        outer['To'] = self.recipients
        outer['From'] = from_name
        #api.portal.get_registry_record('plone.email_from_address')
        outer['Subject'] =  interpolator(self.element.subject)
        outer.epilogue = ''

        # Attach text part
        #text_part = MIMEText('body_plain', 'plain', _charset='UTF-8')
        html_part = MIMEMultipart('related')
        html_text = MIMEText(message, 'html', _charset='UTF-8')
        html_part.attach(html_text)

        outer.attach(html_part)
        mailhost.send(outer.as_string())
        
        # # Finally send mail.
        mailhost.send(outer.as_string())

        
        return True

    def get_recipients(self):
        portal_membership = getToolByName(aq_inner(self.context), "portal_membership")
        portal_groups = getToolByName(aq_inner(self.context), "portal_groups")

        members = set()

        if self.element.members:
            members = set(self.element.members)

        recipients = set()

        for groupId in self.element.groups:
            group = portal_groups.getGroupById(groupId)

            if group and group.getProperties().get("email"):
                recipients.update([group.getProperties().get("email")])

            groupMembers = group.getGroupMemberIds()
            for memberId in groupMembers:
                members.update([memberId])

        for memberId in members:
            member = portal_membership.getMemberById(memberId)
            if member and member.getProperty("email"):
                recipients.update([member.getProperty("email")])

        return recipients

    def create_mime_msg(self):
        # Convert set of recipients to a list:
        list_of_recipients = self.recipients
        if not list_of_recipients:
            return False
        # Prepare multi-part-message to send html with plain-text-fallback-message,
        # for non-html-capable-mail-clients.
        # Thanks to Peter Bengtsson for valuable information about this in this post:
        # http://www.peterbe.com/plog/zope-html-emails
        mime_msg = MIMEMultipart("related")
        mime_msg["Subject"] = self.subject
        mime_msg["From"] = self.source
        # mime_msg['To'] = ''
        mime_msg["Bcc"] = ", ".join(list_of_recipients)
        mime_msg.preamble = "This is a multi-part message in MIME format."

        # Encapsulate the plain and HTML versions of the message body
        # in an 'alternative' part, so message agents can decide
        # which they want to display.
        msgAlternative = MIMEMultipart("alternative")
        mime_msg.attach(msgAlternative)

        # Convert html-message to plain text.
        transforms = getToolByName(aq_inner(self.context), "portal_transforms")
        stream = transforms.convertTo("text/plain", self.message, mimetype="text/html")
        body_plain = stream.getData().strip()

        # We attach the plain text first, the order is mandatory.
        msg_txt = MIMEText(body_plain, _subtype="plain", _charset=self.email_charset)
        msgAlternative.attach(msg_txt)

        # After that, attach html.
        msg_txt = MIMEText(self.message, _subtype="html", _charset=self.email_charset)
        msgAlternative.attach(msg_txt)

        return mime_msg


class MailGroupAddForm(ActionAddForm):
    """An add form for the mail group action"""

    schema = IMailGroupAction
    label = _("Add Mail Group Action")
    description = _("A mail action can mail different groups and members.")
    form_name = _("Configure element")
    Type = MailGroupAction
    # custom template will allow us to add help text
    template = ViewPageTemplateFile("templates/mail.pt")


class MailGroupAddFormView(ContentRuleFormWrapper):
    form = MailGroupAddForm


class MailGroupEditForm(ActionEditForm):
    """An edit form for the mail group action"""

    schema = IMailGroupAction
    label = _("Edit Mail group Action")
    description = _("A mail action can mail different recipient.")
    form_name = _("Configure element")

    # custom template will allow us to add help text
    template = ViewPageTemplateFile("templates/mail.pt")


class MailGroupEditFormView(ContentRuleFormWrapper):
    form = MailGroupEditForm
