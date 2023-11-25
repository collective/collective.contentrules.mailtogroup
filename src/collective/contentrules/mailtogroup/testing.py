from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing.zope import WSGI_SERVER_FIXTURE

import collective.contentrules.mailtogroup


class CollectiveContentrulesMailtogroupLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity
        import plone.restapi

        self.loadZCML(package=plone.app.dexterity)
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=collective.contentrules.mailtogroup)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "collective.contentrules.mailtogroup:default")


COLLECTIVE_CONTENTRULES_MAILTOGROUP_FIXTURE = CollectiveContentrulesMailtogroupLayer()


COLLECTIVE_CONTENTRULES_MAILTOGROUP_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_CONTENTRULES_MAILTOGROUP_FIXTURE,),
    name="CollectiveContentrulesMailtogroupLayer:IntegrationTesting",
)


COLLECTIVE_CONTENTRULES_MAILTOGROUP_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_CONTENTRULES_MAILTOGROUP_FIXTURE,),
    name="CollectiveContentrulesMailtogroupLayer:FunctionalTesting",
)


COLLECTIVE_CONTENTRULES_MAILTOGROUP_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_CONTENTRULES_MAILTOGROUP_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        WSGI_SERVER_FIXTURE,
    ),
    name="CollectiveContentrulesMailtogroupLayer:AcceptanceTesting",
)
