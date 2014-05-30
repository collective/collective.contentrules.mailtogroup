from email import message_from_string
from Products.MailHost.MailHost import MailHost


class DummyMailHost(MailHost):
    """ Modified DummyMailHost from
    plone.app.contentrules.tests.test_action_mail.DummyMailhost.

    This dummy also stores mfrom and mto, so the BCC is checkable
    in the To header.
    """
    meta_type = 'Dummy Mail Host'

    def __init__(self, id):
        self.id = id
        self.sent = []

    def _send(self, mfrom, mto, messageText, *args, **kw):
        msg = message_from_string(messageText)
        sent_msg = dict(
            mfrom=mfrom,
            mto=mto,
            msg=msg
        )
        self.sent.append(sent_msg)