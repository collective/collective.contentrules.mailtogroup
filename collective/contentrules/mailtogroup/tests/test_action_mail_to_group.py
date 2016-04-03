# -*- coding: UTF-8 -*-
import re

from collective.contentrules.mailtogroup.actions.mail import MailGroupAction
from collective.contentrules.mailtogroup.actions.mail import MailGroupAddFormView
from collective.contentrules.mailtogroup.actions.mail import MailGroupEditFormView
from collective.contentrules.mailtogroup.tests.dummymailhost import MockMailHost  # noqa
from email import message_from_string
from email.Message import Message
from plone.app.contentrules.rule import Rule
from plone.app.contentrules.tests.base import ContentRulesTestCase
from plone.app.contentrules.tests.test_action_mail import DummyEvent
from plone.app.testing import FunctionalTesting
from plone.app.testing.bbb import PloneTestCaseFixture
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction, IExecutable
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IMailSchema
from Products.MailHost.interfaces import IMailHost
from Products.PloneTestCase.setup import default_user
from zope.component import getMultiAdapter
from zope.component import getSiteManager
from zope.component import getUtility
from zope.component.interfaces import IObjectEvent


class TestMailToGroupFixture(PloneTestCaseFixture):

    def setUpZope(self, app, configurationContext):
        super(TestMailToGroupFixture,
              self).setUpZope(app, configurationContext)
        import collective.contentrules.mailtogroup
        self.loadZCML(package=collective.contentrules.mailtogroup)

MailToGroupFixture = TestMailToGroupFixture()
TestMailToGroupLayer = FunctionalTesting(bases=(MailToGroupFixture,),
                                         name='TestMailToGroup:Functional')


class TestMailAction(ContentRulesTestCase):

    layer = TestMailToGroupLayer

    def afterSetUp(self):
        self.setRoles(('Manager', ))
        self.portal.invokeFactory('Folder', 'target')
        self.folder.invokeFactory('Document', 'd1',
                                  title=unicode('Wälkommen', 'utf-8'))

        # set up default user and portal owner
        member = self.portal.portal_membership.getMemberById(default_user)
        member.setMemberProperties(dict(email="default@dummy.org"))
        member = self.portal.portal_membership.getMemberById(SITE_OWNER_NAME)
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

    def _setup_mockmail(self):
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = MockMailHost('MailHost')
        sm.registerUtility(dummyMailHost, IMailHost)
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = dummyMailHost
        return dummyMailHost

    def testRegistered(self):
        element = getUtility(IRuleAction, name='plone.actions.MailGroup')
        self.assertEquals('plone.actions.MailGroup', element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(None, element.for_)
        self.assertEquals(None, element.event)

    def testInvokeAddView(self):
        element = getUtility(IRuleAction, name='plone.actions.MailGroup')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')

        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST),
                                  name=element.addview)
        self.failUnless(isinstance(addview, MailGroupAddFormView))

        addview.form_instance.update()
        output = addview.form_instance()
        self.assertIn('<h1>Substitutions</h1>', output)
        content = addview.form_instance.create(data={'subject': 'My Subject',
                                                     'source': 'foo@bar.be',
                                                     'groups': ['group1', 'group2'],
                                                     'members': [default_user, ],
                                                     'message': 'Hey, Oh!'})
        addview.form_instance.add(content)
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
        self.failUnless(isinstance(editview, MailGroupEditFormView))

    def testExecute(self):
        self.loginAsPortalOwner()
        dummyMailHost = self._setup_mockmail()
        e = MailGroupAction()
        e.source = "foo@bar.be"
        e.groups = ['group1', ]
        e.message = u"Päge '${title}' created in ${url} !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()
        mailSent = message_from_string(dummyMailHost.messages[0]['msg'])
        mailTo = dummyMailHost.messages[0]['mto'][0]
        mailType = mailSent.get('Content-Type')
        self.assertTrue(mailType.startswith('multipart/related'))
        self.assertEqual('member1@dummy.org', mailTo)
        self.assertEqual("foo@bar.be", mailSent.get('From'))
        self.assertIn("P=C3=A4ge \'W=C3=A4lkommen\' created in http://nohost/plone/Members/test_user=\n_1_/d1",
                      mailSent.get_payload(0).as_string())

    def testExecuteNoSource(self):
        self.loginAsPortalOwner()
        dummyMailHost = self._setup_mockmail()
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema,
                                              prefix='plone')

        e = MailGroupAction()
        e.groups = ['group1', ]
        e.message = 'Document created !'
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ret = ex()
        self.assertFalse(ret)
        # if we provide a site mail address this won't fail anymore
        mail_settings.email_from_address = 'manager@portal.be'
        mail_settings.email_from_name = u'manager'
        ret = ex()

        mailSent = message_from_string(dummyMailHost.messages[0]['msg'])
        mailTo = dummyMailHost.messages[0]['mto'][0]
        mailFrom = mailSent.get('From')
        mailType = mailSent.get('Content-Type')
        self.assertTrue(mailType.startswith('multipart/related'))
        self.assertIn("member1@dummy.org", mailTo)
        self.assertIn("manager@portal.be", mailFrom)
        self.assertIn('Document created !', str(mailSent))

    def testExecuteMultiGroupsAndUsers(self):
        self.loginAsPortalOwner()
        dummyMailHost = self._setup_mockmail()

        e = MailGroupAction()
        e.source = "foo@bar.be"
        e.groups = ['group1', 'group2']
        e.members = [SITE_OWNER_NAME, default_user, ]
        e.message = 'Document created !'
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()

        mailSent = message_from_string(dummyMailHost.messages[0]['msg'])
        mailTo = dummyMailHost.messages[0]['mto']
        mailFrom = mailSent.get('From')
        mailType = mailSent.get('Content-Type')
        self.assertEqual(len(mailTo), 4)
        self.failUnless(isinstance(mailSent, Message))
        self.assertTrue(mailType.startswith('multipart/related'))

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
