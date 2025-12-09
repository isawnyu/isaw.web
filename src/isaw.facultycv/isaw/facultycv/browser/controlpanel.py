from plone.app.registry.browser import controlpanel
from collective.z3cform.datagridfield.datagridfield import DataGridFieldFactory

from ..interfaces.settings import IISAWFacultyCVSettings


class ISAWFacultyCVSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IISAWFacultyCVSettings
    label = u"ISAW FacultyCV Settings"
    description = u""
    enableCSRFProtection = True

    def updateFields(self):
        super(ISAWFacultyCVSettingsEditForm, self).updateFields()
        self.fields['named_locations'].widgetFactory = DataGridFieldFactory


class ISAWFacultyCVControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ISAWFacultyCVSettingsEditForm
