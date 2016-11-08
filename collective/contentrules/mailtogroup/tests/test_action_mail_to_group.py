# -*- coding: UTF-8 -*-
from collective.contentrules.mailtogroup.tests.dummymailhost import MockMailHost  # noqa
from email import message_from_string
from email.Message import Message
from plone import api
from plone.app.contentrules.rule import Rule
from plone.app.contentrules.tests.base import ContentRulesTestCase
from plone.app.contentrules.tests.test_action_mail import DummyEvent
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing.bbb import _createMemberarea
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleAction
from Products.CMFCore.utils import getToolByName
from Products.MailHost.interfaces import IMailHost
from Products.PloneTestCase.setup import default_user
from zope.component import getMultiAdapter
from zope.component import getSiteManager
from zope.component import getUtility

import pkg_resources
import transaction


try:
    pkg_resources.get_distribution('plone.app.contenttypes')
except pkg_resources.DistributionNotFound:
    from plone.app.testing import PLONE_FIXTURE
    CT_PROFILE = ''
else:
    from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE as PLONE_FIXTURE
    CT_PROFILE = 'plone.app.contenttypes:default'


IS_PLONE_5 = api.env.plone_version().startswith('5')

if IS_PLONE_5:
    from collective.contentrules.mailtogroup.actions.mail import MailGroupAction
    from collective.contentrules.mailtogroup.actions.mail import MailGroupAddFormView
    from collective.contentrules.mailtogroup.actions.mail import MailGroupEditFormView
else:
    from collective.contentrules.mailtogroup.actions_formlib.mail import MailGroupAction
    from collective.contentrules.mailtogroup.actions_formlib.mail import MailGroupAddForm as MailGroupAddFormView
    from collective.contentrules.mailtogroup.actions_formlib.mail import MailGroupEditForm as MailGroupEditFormView


class TestMailToGroupFixture(PloneSandboxLayer):

    default_bases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.contentrules.mailtogroup
        self.loadZCML(package=collective.contentrules.mailtogroup)

    def setUpPloneSite(self, portal):
        if CT_PROFILE:
            self.applyProfile(portal, CT_PROFILE)

MailToGroupFixture = TestMailToGroupFixture()
TestMailToGroupLayer = IntegrationTesting(bases=(MailToGroupFixture,),
                                          name='TestMailToGroup:Integration')


class TestMailAction(ContentRulesTestCase):

    layer = TestMailToGroupLayer

    def setUp(self):
        """ The setup steps below are only needed in Plone 5,
        because in Plone 4 they are taken care of automatically
        by PloneTestCase.
        """
        if IS_PLONE_5:
            self.portal = self.layer['portal']
            setRoles(self.portal, TEST_USER_ID, ['Manager'])
            _createMemberarea(self.portal, TEST_USER_ID)
            self.folder = self.portal.portal_membership.getHomeFolder(TEST_USER_ID)
            transaction.commit()
            self.afterSetUp()
        else:
            super(TestMailAction, self).setUp()

    def afterSetUp(self):
        """ This method is only run by PloneTestCase, i.e. in Plone 4.
        Thus, we want to call it from setUp() in Plone 5.
        """
        self.setRoles(('Manager', ))
        self.folder.invokeFactory('Document', 'd1',
                                  title=unicode('Wälkommen', 'utf-8'))

        # set up default user and portal owner
        member = self.portal.portal_membership.getMemberById(default_user)
        member.setMemberProperties(dict(email='default@dummy.org'))
        member = self.portal.portal_membership.getMemberById(SITE_OWNER_NAME)
        member.setMemberProperties(dict(email='portal@dummy.org'))

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

        groups.addGroup('group3')

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
        self.assertEqual('plone.actions.MailGroup', element.addview)
        self.assertEqual('edit', element.editview)
        self.assertEqual(None, element.for_)
        self.assertEqual(None, element.event)

    def testInvokeAddView(self):
        element = getUtility(IRuleAction, name='plone.actions.MailGroup')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')

        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST),
                                  name=element.addview)
        self.assertTrue(isinstance(addview, MailGroupAddFormView))

        if IS_PLONE_5:
            addview.form_instance.update()
            output = addview.form_instance()
            self.assertIn('<h1>Substitutions</h1>', output)
            content = addview.form_instance.create(data={'subject': 'My Subject',
                                                         'source': 'foo@bar.be',
                                                         'groups': ['group1', 'group2'],
                                                         'members': [default_user, ],
                                                         'message': 'Hey, Oh!'})
            addview.form_instance.add(content)
        else:
            addview.createAndAdd(data={'subject': 'My Subject',
                                       'source': 'foo@bar.be',
                                       'groups': ['group1', 'group2'],
                                       'members': [default_user, ],
                                       'message': 'Hey, Oh!'})

        e = rule.actions[0]
        self.assertTrue(isinstance(e, MailGroupAction))
        self.assertEqual('My Subject', e.subject)
        self.assertEqual('foo@bar.be', e.source)
        self.assertEqual(['group1', 'group2'], e.groups)
        self.assertEqual([default_user, ], e.members)
        self.assertEqual('Hey, Oh!', e.message)

    def testInvokeEditView(self):
        element = getUtility(IRuleAction, name='plone.actions.MailGroup')
        e = MailGroupAction()
        editview = getMultiAdapter((e, self.folder.REQUEST),
                                   name=element.editview)
        self.assertTrue(isinstance(editview, MailGroupEditFormView))

    def testExecute(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        dummyMailHost = self._setup_mockmail()
        e = MailGroupAction()
        e.source = 'foo@bar.be'
        e.groups = ['group1', ]
        e.message = u'Päge \'${title}\' created in ${url} !'
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()
        mailSent = message_from_string(dummyMailHost.messages[0]['msg'])
        mailTo = dummyMailHost.messages[0]['mto'][0]
        mailType = mailSent.get('Content-Type')
        self.assertTrue(mailType.startswith('multipart/related'))
        self.assertEqual('member1@dummy.org', mailTo)
        self.assertEqual('foo@bar.be', mailSent.get('From'))
        self.assertIn('P=C3=A4ge \'W=C3=A4lkommen\' created in http://nohost/plone/Members/test_user=\n_1_/d1',
                      mailSent.get_payload(0).as_string())

    def testExecuteNoSource(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        dummyMailHost = self._setup_mockmail()

        e = MailGroupAction()
        e.groups = ['group1', ]
        e.message = 'Document created !'
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        if IS_PLONE_5:
            ret = ex()
            self.assertFalse(ret)
        else:
            self.assertRaises(ValueError, ex)

        # if we provide a site mail address this won't fail anymore
        if IS_PLONE_5:
            from plone.registry.interfaces import IRegistry
            from Products.CMFPlone.interfaces import IMailSchema
            registry = getUtility(IRegistry)
            mail_settings = registry.forInterface(IMailSchema,
                                                  prefix='plone')

            mail_settings.email_from_address = 'manager@portal.be'
            mail_settings.email_from_name = u'manager'
        else:
            sm = getSiteManager(self.portal)
            sm.manage_changeProperties({'email_from_address': 'manager@portal.be'})

        ret = ex()

        mailSent = message_from_string(dummyMailHost.messages[0]['msg'])
        mailTo = dummyMailHost.messages[0]['mto'][0]
        mailFrom = mailSent.get('From')
        mailType = mailSent.get('Content-Type')
        self.assertTrue(mailType.startswith('multipart/related'))
        self.assertIn('member1@dummy.org', mailTo)
        self.assertIn('manager@portal.be', mailFrom)
        self.assertIn('Document created !', str(mailSent))

    def testExecuteMultiGroupsAndUsers(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        dummyMailHost = self._setup_mockmail()

        e = MailGroupAction()
        e.source = 'foo@bar.be'
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
        self.assertTrue(isinstance(mailSent, Message))
        self.assertTrue(mailType.startswith('multipart/related'))

        self.assertEqual('foo@bar.be', mailFrom)
        self.assertIn('default@dummy.org', mailTo)
        self.assertIn('portal@dummy.org', mailTo)
        self.assertIn('member1@dummy.org', mailTo)
        self.assertIn('member2@dummy.org', mailTo)
        self.assertIn('Document created !', str(mailSent))

    def testExecuteEmptyGroup(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        dummyMailHost = self._setup_mockmail()

        e = MailGroupAction()
        e.source = 'foo@bar.be'
        e.groups = ['group3']
        e.members = []
        e.message = 'Document created !'
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ret = ex()

        self.assertFalse(ret)

        self.assertEqual(len(dummyMailHost.messages), 0)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMailAction))
    return suite
