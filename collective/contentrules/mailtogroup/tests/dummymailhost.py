# -*- coding: UTF-8 -*-
from Products.CMFPlone.tests.utils import MockMailHost as MailBase
from Products.MailHost.MailHost import _mungeHeaders


class MockMailHost(MailBase):
    """A MailHost that collects messages instead of sending them.
       This mock also stores mto, so the BCC is checkable
       in the To header.
    """

    def send(self, messageText, mto=None, mfrom=None, subject=None,
             encode=None, immediate=False, charset=None, msg_type=None):
        messageText, mto, mfrom = _mungeHeaders(messageText,
                                                mto, mfrom, subject,
                                                charset=charset,
                                                msg_type=msg_type)
        self.messages.append(dict(msg=messageText, mto=mto))
