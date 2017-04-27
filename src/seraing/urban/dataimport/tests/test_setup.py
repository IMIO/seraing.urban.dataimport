# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from seraing.urban.dataimport.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of seraing.urban.dataimport into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if seraing.urban.dataimport is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('seraing.urban.dataimport'))

    def test_uninstall(self):
        """Test if seraing.urban.dataimport is cleanly uninstalled."""
        self.installer.uninstallProducts(['seraing.urban.dataimport'])
        self.assertFalse(self.installer.isProductInstalled('seraing.urban.dataimport'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that ISeraingUrbanDataimportLayer is registered."""
        from seraing.urban.dataimport.interfaces import ISeraingUrbanDataimportLayer
        from plone.browserlayer import utils
        self.failUnless(ISeraingUrbanDataimportLayer in utils.registered_layers())
