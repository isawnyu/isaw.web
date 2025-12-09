from .interfaces import IISAWSettings
from plone.app.registry.browser import controlpanel

class ISAWSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IISAWSettings
    label = "ISAW Settings"
    description = "Custom settings for ISAW web site."

    def updateFields(self):
        super(ISAWSettingsEditForm, self).updateFields()


class ISAWSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ISAWSettingsEditForm
