from collective.contentrules.mailtogroup.tests.dummymailhost import MockMailHost  # noqa
from email import message_from_string
from email.message import Message
from plone import api
from plone.app.contentrules.rule import Rule
from plone.app.contentrules.tests.base import ContentRulesTestCase
from plone.app.contentrules.tests.test_action_mail import DummyEvent
from plone.app.testing import (
    FunctionalTesting,
    PloneSandboxLayer,
    setRoles,
    TEST_USER_ID,
)
from plone.app.testing.bbb import _createMemberarea
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IExecutable, IRuleAction
from Products.CMFCore.utils import getToolByName
from Products.MailHost.interfaces import IMailHost
from zope.component import getMultiAdapter, getSiteManager, getUtility

import pkg_resources
import transaction


try:
    pkg_resources.get_distribution("plone.app.contenttypes")
except pkg_resources.DistributionNotFound:
    from plone.app.testing import PLONE_FIXTURE

    CT_PROFILE = ""
else:
    from plone.app.contenttypes.testing import (
        PLONE_APP_CONTENTTYPES_FIXTURE as PLONE_FIXTURE,
    )

    CT_PROFILE = "plone.app.contenttypes:default"


from collective.contentrules.mailtogroup.actions.mail import (
    MailGroupAction,
    MailGroupAddFormView,
    MailGroupEditFormView,
)


class TestMailToGroupFixture(PloneSandboxLayer):

    default_bases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.contentrules.mailtogroup

        self.loadZCML(package=collective.contentrules.mailtogroup)

    def setUpPloneSite(self, portal):
        if CT_PROFILE:
            self.applyProfile(portal, CT_PROFILE)


MailToGroupFixture = TestMailToGroupFixture()
TestMailToGroupLayer = FunctionalTesting(
    bases=(MailToGroupFixture,), name="TestMailToGroup:Functionial"
)


class TestMailAction(ContentRulesTestCase):

    layer = TestMailToGroupLayer

    def setUp(self):
        """The setup for Plone 5.
        """
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        _createMemberarea(self.portal, TEST_USER_ID)
        self.folder = self.portal.portal_membership.getHomeFolder(TEST_USER_ID)
        transaction.commit()
        self.afterSetUp()

    def afterSetUp(self):
        """This method will be called from setUp() in Plone 5.
        """
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.folder.invokeFactory("Document", "d1", title="Wälkommen")

        # set up default user and portal owner
        member = self.portal.portal_membership.getMemberById(TEST_USER_ID)
        member.setMemberProperties(dict(email="default@dummy.org"))
        member = self.portal.portal_membership.getMemberById(SITE_OWNER_NAME)
        member.setMemberProperties(dict(email="portal@dummy.org"))

        membership = getToolByName(self.portal, "portal_membership")

        membership.addMember(
            "member1",
            "secret",
            ("Member",),
            (),
            properties={"email": "member1@dummy.org"},
        )

        membership.addMember(
            "member2",
            "secret",
            ("Member",),
            (),
            properties={"email": "member2@dummy.org"},
        )

        # empty e-mail address
        membership.addMember(
            "member3", "secret", ("Member",), (), properties={"email": ""}
        )

        groups = getToolByName(self.portal, "portal_groups")

        groups.addGroup("group1")
        groups.addPrincipalToGroup("member1", "group1")

        groups.addGroup("group2")
        groups.addPrincipalToGroup("member2", "group2")
        groups.addPrincipalToGroup("member3", "group2")

        groups.addGroup("group3")

    def _setup_mockmail(self):
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = MockMailHost("MailHost")
        sm.registerUtility(dummyMailHost, IMailHost)
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = dummyMailHost
        return dummyMailHost

    def testRegistered(self):
        element = getUtility(IRuleAction, name="plone.actions.MailGroup")
        self.assertEqual("plone.actions.MailGroup", element.addview)
        self.assertEqual("edit", element.editview)
        self.assertEqual(None, element.for_)
        self.assertEqual(None, element.event)

    def testInvokeAddView(self):
        element = getUtility(IRuleAction, name="plone.actions.MailGroup")
        storage = getUtility(IRuleStorage)
        storage["foo"] = Rule()
        rule = self.portal.restrictedTraverse("++rule++foo")

        adding = getMultiAdapter((rule, self.portal.REQUEST), name="+action")
        addview = getMultiAdapter((adding, self.portal.REQUEST), name=element.addview)
        self.assertTrue(isinstance(addview, MailGroupAddFormView))

        addview.form_instance.update()
        output = addview.form_instance()
        self.assertIn("<h1>Substitutions</h1>", output)
        content = addview.form_instance.create(
            data={
                "subject": "My Subject",
                "source": "foo@bar.be",
                "groups": ["group1", "group2"],
                "members": [TEST_USER_ID],
                "message": "Hey, Oh!",
            }
        )
        addview.form_instance.add(content)

        e = rule.actions[0]
        self.assertTrue(isinstance(e, MailGroupAction))
        self.assertEqual("My Subject", e.subject)
        self.assertEqual("foo@bar.be", e.source)
        self.assertEqual(["group1", "group2"], e.groups)
        self.assertEqual([TEST_USER_ID], e.members)
        self.assertEqual("Hey, Oh!", e.message)

    def testInvokeEditView(self):
        element = getUtility(IRuleAction, name="plone.actions.MailGroup")
        e = MailGroupAction()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.assertTrue(isinstance(editview, MailGroupEditFormView))

    def testExecute(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        dummyMailHost = self._setup_mockmail()
        e = MailGroupAction()
        e.source = "foo@bar.be"
        e.groups = ["group1"]
        e.message = "Päge '${title}' created in ${url} !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        ex()
        mailSent = message_from_string(dummyMailHost.messages[0]["msg"].decode())
        mailTo = dummyMailHost.messages[0]["mto"][0]
        mailType = mailSent.get("Content-Type")
        self.assertTrue(mailType.startswith("multipart/related"))
        self.assertEqual("member1@dummy.org", mailTo)
        self.assertEqual("foo@bar.be", mailSent.get("From"))
        self.assertIn(
            "P=C3=A4ge 'W=C3=A4lkommen' created in http://nohost/plone/Members/test_user=\n_1_/d1",
            mailSent.get_payload(0).as_string(),
        )

    def testExecuteNoSource(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        dummyMailHost = self._setup_mockmail()

        e = MailGroupAction()
        e.groups = ["group1"]
        e.message = "Document created !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        ret = ex()
        self.assertFalse(ret)

        # if we provide a site mail address this won't fail anymore
        from plone.registry.interfaces import IRegistry
        from Products.CMFPlone.interfaces import IMailSchema

        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")

        mail_settings.email_from_address = "manager@portal.be"
        mail_settings.email_from_name = "manager"

        ret = ex()

        mailSent = message_from_string(dummyMailHost.messages[0]["msg"].decode())
        mailTo = dummyMailHost.messages[0]["mto"][0]
        mailFrom = mailSent.get("From")
        mailType = mailSent.get("Content-Type")
        self.assertTrue(mailType.startswith("multipart/related"))
        self.assertIn("member1@dummy.org", mailTo)
        self.assertIn("manager@portal.be", mailFrom)
        self.assertIn("Document created !", str(mailSent))

    def testExecuteMultiGroupsAndUsers(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        dummyMailHost = self._setup_mockmail()

        e = MailGroupAction()
        e.source = "foo@bar.be"
        e.groups = ["group1", "group2"]
        e.members = [SITE_OWNER_NAME, TEST_USER_ID]
        e.message = "Document created !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        ex()

        mailSent = message_from_string(dummyMailHost.messages[0]["msg"].decode())
        mailTo = dummyMailHost.messages[0]["mto"]
        mailFrom = mailSent.get("From")
        mailType = mailSent.get("Content-Type")
        self.assertEqual(len(mailTo), 4)
        self.assertTrue(isinstance(mailSent, Message))
        self.assertTrue(mailType.startswith("multipart/related"))

        self.assertEqual("foo@bar.be", mailFrom)
        self.assertIn("default@dummy.org", mailTo)
        self.assertIn("portal@dummy.org", mailTo)
        self.assertIn("member1@dummy.org", mailTo)
        self.assertIn("member2@dummy.org", mailTo)
        self.assertIn("Document created !", str(mailSent))

    def testExecuteEmptyGroup(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        dummyMailHost = self._setup_mockmail()

        e = MailGroupAction()
        e.source = "foo@bar.be"
        e.groups = ["group3"]
        e.members = []
        e.message = "Document created !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        ret = ex()

        self.assertFalse(ret)

        self.assertEqual(len(dummyMailHost.messages), 0)


def test_suite():
    from unittest import makeSuite, TestSuite

    suite = TestSuite()
    suite.addTest(makeSuite(TestMailAction))
    return suite
