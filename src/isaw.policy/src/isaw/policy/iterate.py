from AccessControl import getSecurityManager
from Acquisition import aq_inner
from plone.app.iterate.browser.control import Control
from plone.app.iterate.browser.control import ICheckinCheckoutPolicy
from plone.app.iterate import interfaces
from plone.app.iterate import permissions


class ISAWIterateControl(Control):
    """Override Iterate control"""

    def get_original(self, context):

        policy = ICheckinCheckoutPolicy(self.context, None)
        if policy is None:
            return None
        original = policy.getBaseline()
        return original


    def checkin_allowed(self):
        """Check if a checkin is allowed
        """
        context = aq_inner(self.context)
        checkPermission = getSecurityManager().checkPermission

        if not interfaces.IIterateAware.providedBy(context):
            return False

        archiver = interfaces.IObjectArchiver(context)
        if not archiver.isVersionable():
            return False

        original = self.get_original(context)
        if original is None:
            return False

        if not checkPermission(permissions.CheckinPermission, original):
            return False

        return True
