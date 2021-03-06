import unittest2 as unittest
from Products.CMFCore.utils import getToolByName
from isaw.policy.testing import ISAW_POLICY_INTEGRATION_TESTING

from isaw.policy import config


class TestInstallation(unittest.TestCase):

    layer = ISAW_POLICY_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')

    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product
            installed
        """
        pid = 'isaw.policy'
        installed = [p['id'] for p in self.qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                        'package appears not to have been installed')

    def testIS_PRODUCTION_globalIsFalseInTests(self):
        self.assertFalse(
            config.IS_PRODUCTION,
            'We should not think we are running in production!'
        )
