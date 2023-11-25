"""Setup tests for this package."""
from collective.contentrules.mailtogroup.testing import (
    COLLECTIVE_CONTENTRULES_MAILTOGROUP_INTEGRATION_TESTING,
)
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.base.utils import get_installer

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.contentrules.mailtogroup is properly installed."""

    layer = COLLECTIVE_CONTENTRULES_MAILTOGROUP_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.installer = get_installer(self.portal, self.layer["request"])

    def test_product_installed(self):
        """Test if collective.contentrules.mailtogroup is installed."""
        self.assertTrue(
            self.installer.is_product_installed("collective.contentrules.mailtogroup")
        )

    def test_browserlayer(self):
        """Test that ICollectiveContentrulesMailtogroupLayer is registered."""
        from collective.contentrules.mailtogroup.interfaces import (
            ICollectiveContentrulesMailtogroupLayer,
        )
        from plone.browserlayer import utils

        self.assertIn(
            ICollectiveContentrulesMailtogroupLayer, utils.registered_layers()
        )


class TestUninstall(unittest.TestCase):
    layer = COLLECTIVE_CONTENTRULES_MAILTOGROUP_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])

        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstall_product("collective.contentrules.mailtogroup")
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if collective.contentrules.mailtogroup is cleanly uninstalled."""
        self.assertFalse(
            self.installer.is_product_installed("collective.contentrules.mailtogroup")
        )

    def test_browserlayer_removed(self):
        """Test that ICollectiveContentrulesMailtogroupLayer is removed."""
        from collective.contentrules.mailtogroup.interfaces import (
            ICollectiveContentrulesMailtogroupLayer,
        )
        from plone.browserlayer import utils

        self.assertNotIn(
            ICollectiveContentrulesMailtogroupLayer, utils.registered_layers()
        )
