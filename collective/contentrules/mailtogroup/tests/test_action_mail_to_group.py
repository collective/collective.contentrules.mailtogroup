# -*- coding: UTF-8 -*-

from email.MIMEText import MIMEText
from zope.component import getUtility, getMultiAdapter, getSiteManager
from zope.component.interfaces import IObjectEvent
from zope.interface import implements

from plone.app.contentrules.rule import Rule
from plone.app.contentrules.tests.base import ContentRulesTestCase
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction, IExecutable
from collective.contentrules.mailtogroup.actions.mail import MailGroupAction, MailGroupEditForm, MailGroupAddForm

from Products.CMFCore.utils import getToolByName

from Products.MailHost.interfaces import IMailHost
from Products.SecureMailHost.SecureMailHost import SecureMailHost

from Products.PloneTestCase.setup import default_user


# basic test structure copied from plone.app.contentrules test_action_mail.py

class DummyEvent(object):
    implements(IObjectEvent)

    def __init__(self, object):
        self.object = object

class DummySecureMailHost(SecureMailHost):
    meta_type = 'Dummy secure Mail Host'
    def __init__(self, id):
        self.id = id
        self.sent = []

    def _send(self, mfrom, mto, messageText, debug=False):
        self.sent.append(messageText)


class TestMailAction(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('Folder', 'target')
        self.folder.invokeFactory('Document', 'd1',
            title=unicode('Wälkommen', 'utf-8'))
        
        # set up default user and portal owner
        member = self.portal.portal_membership.getMemberById(default_user)
        member.setMemberProperties(dict(email="default@dummy.org"))
        member = self.portal.portal_membership.getMemberById('portal_owner')
        member.setMemberProperties(dict(email="portal@dummy.org"))

        membership = getToolByName(self.portal, 'portal_membership')

        membership.addMember(
            'member1',
            'secret',
            ('Member',),
            (),
            properties={'email':'member1@dummy.org'})
            
        membership.addMember(
            'member2',
            'secret',
            ('Member',),
            (),
            properties={'email':'member2@dummy.org'})

        # empty e-mail address 
        membership.addMember(
            'member3',
            'secret',
            ('Member',),
            (),
            properties={'email':''})
     
        groups = getToolByName(self.portal, 'portal_groups')

        groups.addGroup('group1')
        groups.addPrincipalToGroup('member1', 'group1')
         
        groups.addGroup('group2')
        groups.addPrincipalToGroup('member2', 'group2')
        groups.addPrincipalToGroup('member3', 'group2')



    def testRegistered(self):
        element = getUtility(IRuleAction, name='plone.actions.MailGroup')
        self.assertEquals('plone.actions.MailGroup', element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(None, element.for_)
        self.assertEquals(IObjectEvent, element.event)

    def testInvokeAddView(self):
        element = getUtility(IRuleAction, name='plone.actions.MailGroup')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')

        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST),
                                  name=element.addview)
        self.failUnless(isinstance(addview,MailGroupAddForm))

        addview.createAndAdd(data={'subject' : 'My Subject',
                                   'source': 'foo@bar.be',
                                   'groups' : ['group1', 'group2'],
                                   'members' : [default_user,],
                                   'message': 'Hey, Oh!'})

        e = rule.actions[0]
        self.failUnless(isinstance(e, MailGroupAction))
        self.assertEquals('My Subject', e.subject)
        self.assertEquals('foo@bar.be', e.source)
        self.assertEquals(['group1', 'group2'], e.groups)
        self.assertEquals([default_user,], e.members)
        self.assertEquals('Hey, Oh!', e.message)

    def testInvokeEditView(self):
        element = getUtility(IRuleAction, name='plone.actions.MailGroup')
        e = MailGroupAction()
        editview = getMultiAdapter((e, self.folder.REQUEST),
                                   name=element.editview)
        self.failUnless(isinstance(editview, MailGroupEditForm))

    def testExecute(self):
        self.loginAsPortalOwner()
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummySecureMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        e = MailGroupAction()
        e.source = "foo@bar.be"
        e.groups = ['group1',]
        e.message = u"Päge '${title}' created in ${url} !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()
        self.failUnless(isinstance(dummyMailHost.sent[0], MIMEText))
        mailSent = dummyMailHost.sent[0]
        self.assertEqual('text/plain; charset="utf-8"',
                        mailSent.get('Content-Type'))
        self.assertEqual("member1@dummy.org", mailSent.get('To'))
        self.assertEqual("foo@bar.be", mailSent.get('From'))
        self.assertEqual("P\xc3\xa4ge 'W\xc3\xa4lkommen' created in \
http://nohost/plone/Members/test_user_1_/d1 !",
                         mailSent.get_payload(decode=True))

    def testExecuteNoSource(self):
        self.loginAsPortalOwner()
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummySecureMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        e = MailGroupAction()
        e.groups = ['group1',]
        e.message = 'Document created !'
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        self.assertRaises(ValueError, ex)
        # if we provide a site mail address this won't fail anymore
        sm.manage_changeProperties({'email_from_address': 'manager@portal.be'})
        ex()
        self.failUnless(isinstance(dummyMailHost.sent[0], MIMEText))
        mailSent = dummyMailHost.sent[0]
        self.assertEqual('text/plain; charset="utf-8"',
                        mailSent.get('Content-Type'))
        self.assertEqual("member1@dummy.org", mailSent.get('To'))
        self.assertEqual("Site Administrator <manager@portal.be>",
                         mailSent.get('From'))
        self.assertEqual("Document created !",
                         mailSent.get_payload(decode=True))

    def testExecuteMultiGroupsAndUsers(self):
        self.loginAsPortalOwner()
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummySecureMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        e = MailGroupAction()
        e.source = "foo@bar.be"
        e.groups = ['group1', 'group2']
        e.members = ['portal_owner', default_user,]
        e.message = 'Document created !'
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()
        self.assertEqual(len(dummyMailHost.sent), 4)
        self.failUnless(isinstance(dummyMailHost.sent[0], MIMEText))
        mailSent = dummyMailHost.sent[0]
        self.assertEqual('text/plain; charset="utf-8"',
                        mailSent.get('Content-Type'))
        self.assertEqual('default@dummy.org', mailSent.get('To'))
        self.assertEqual('foo@bar.be', mailSent.get('From'))
        self.assertEqual('Document created !',mailSent.get_payload(decode=True))
        mailSent = dummyMailHost.sent[1]
        self.assertEqual('text/plain; charset="utf-8"',
                        mailSent.get('Content-Type'))
        self.assertEqual('portal@dummy.org', mailSent.get('To'))
        self.assertEqual('foo@bar.be', mailSent.get('From'))
        self.assertEqual('Document created !',mailSent.get_payload(decode=True))
        mailSent = dummyMailHost.sent[2]
        self.assertEqual('text/plain; charset="utf-8"',
                        mailSent.get('Content-Type'))
        self.assertEqual('member1@dummy.org', mailSent.get('To'))
        self.assertEqual('foo@bar.be', mailSent.get('From'))
        self.assertEqual('Document created !',mailSent.get_payload(decode=True))
        mailSent = dummyMailHost.sent[3]
        self.assertEqual('text/plain; charset="utf-8"',
                        mailSent.get('Content-Type'))
        self.assertEqual('member2@dummy.org', mailSent.get('To'))
        self.assertEqual('foo@bar.be', mailSent.get('From'))
        self.assertEqual('Document created !',mailSent.get_payload(decode=True))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMailAction))
    return suite 
