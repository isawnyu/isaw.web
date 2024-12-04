from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class IsawpolicyLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import isaw.policy
        xmlconfig.file(
            'configure.zcml',
            isaw.policy,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        z2.installProduct(app, 'Products.CMFPlacefulWorkflow')

    def tearDownZope(self, app):
        # Uninstall products installed above
        z2.uninstallProduct(app, 'Products.CMFPlacefulWorkflow')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'isaw.policy:default')

ISAW_POLICY_FIXTURE = IsawpolicyLayer()
ISAW_POLICY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(ISAW_POLICY_FIXTURE,),
    name="IsawpolicyLayer:Integration"
)
ISAW_POLICY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(ISAW_POLICY_FIXTURE, z2.ZSERVER_FIXTURE),
    name="IsawpolicyLayer:Functional"
)
