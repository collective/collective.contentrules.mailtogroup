# -*- coding: UTF-8 -*-

from email.Message import Message
from zope.component import getUtility, getMultiAdapter, getSiteManager
from zope.component.interfaces import IObjectEvent
from zope.interface import implements

from plone.app.contentrules.rule import Rule
from plone.app.contentrules.tests.base import ContentRulesTestCase
from plone.app.contentrules.tests.test_action_mail import DummyEvent
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction, IExecutable
from collective.contentrules.mailtogroup.actions.mail import MailGroupAction, MailGroupEditForm, MailGroupAddForm
from collective.contentrules.mailtogroup.tests.dummymailhost import DummyMailHost

from Products.CMFCore.utils import getToolByName

from Products.MailHost.interfaces import IMailHost

from Products.PloneTestCase.setup import default_user


class TestMailAction(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))
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
            ('Member', ),
            (),
            properties={'email': 'member1@dummy.org'})

        membership.addMember(
            'member2',
            'secret',
            ('Member', ),
            (),
            properties={'email': 'member2@dummy.org'})

        # empty e-mail address
        membership.addMember(
            'member3',
            'secret',
            ('Member', ),
            (),
            properties={'email': ''})

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
        self.failUnless(isinstance(addview, MailGroupAddForm))

        addview.createAndAdd(data={'subject': 'My Subject',
                                   'source': 'foo@bar.be',
                                   'groups': ['group1', 'group2'],
                                   'members': [default_user, ],
                                   'message': 'Hey, Oh!'})

        e = rule.actions[0]
        self.failUnless(isinstance(e, MailGroupAction))
        self.assertEquals('My Subject', e.subject)
        self.assertEquals('foo@bar.be', e.source)
        self.assertEquals(['group1', 'group2'], e.groups)
        self.assertEquals([default_user, ], e.members)
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
        dummyMailHost = DummyMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        e = MailGroupAction()
        e.source = "foo@bar.be"
        e.groups = ['group1', ]
        e.message = u"Päge '${title}' created in ${url} !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()
        self.failUnless(isinstance(dummyMailHost.sent[0]['msg'], Message))
        mailSent = dummyMailHost.sent[0]['msg']
        self.assertTrue(mailSent.get('Content-Type').startswith('multipart/related'))
        self.assertEqual(None, mailSent.get('To'))
        self.assertEqual("foo@bar.be", mailSent.get('From'))
        self.assertIn("P=C3=A4ge \'W=C3=A4lkommen\' created in http://nohost/plone/Members/test_user=\n_1_/d1",
            str(mailSent.get_payload()[0]))

    def testExecuteNoSource(self):
        self.loginAsPortalOwner()
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummyMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        e = MailGroupAction()
        e.groups = ['group1', ]
        e.message = 'Document created !'
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        self.assertRaises(ValueError, ex)
        # if we provide a site mail address this won't fail anymore
        sm.manage_changeProperties({'email_from_address': 'manager@portal.be'})
        ex()
        self.failUnless(isinstance(dummyMailHost.sent[0]['msg'], Message))

        mailSent = dummyMailHost.sent[0]['msg']
        mailTo = dummyMailHost.sent[0]['mto']
        mailFrom = dummyMailHost.sent[0]['mfrom']

        self.assertTrue(mailSent.get('Content-Type').startswith('multipart/related'))
        self.assertIn("member1@dummy.org", mailTo)
        self.assertIn("manager@portal.be", mailFrom)
        self.assertIn('Document created !', str(mailSent))

    def testExecuteMultiGroupsAndUsers(self):
        self.loginAsPortalOwner()
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)

        dummyMailHost = DummyMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)

        e = MailGroupAction()
        e.source = "foo@bar.be"
        e.groups = ['group1', 'group2']
        e.members = ['portal_owner', default_user, ]
        e.message = 'Document created !'
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()

        self.assertEqual(len(dummyMailHost.sent[0]['mto']), 4)
        self.failUnless(isinstance(dummyMailHost.sent[0]['msg'], Message))

        mailSent = dummyMailHost.sent[0]['msg']
        mailTo = dummyMailHost.sent[0]['mto']
        mailFrom = dummyMailHost.sent[0]['mfrom']
        self.assertTrue(mailSent.get('Content-Type').startswith('multipart/related'))

        self.assertEqual('foo@bar.be', mailFrom)
        self.assertIn('default@dummy.org', mailTo)
        self.assertIn('portal@dummy.org', mailTo)
        self.assertIn('member1@dummy.org', mailTo)
        self.assertIn('member2@dummy.org', mailTo)
        self.assertIn('Document created !', str(mailSent))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMailAction))
    return suite
