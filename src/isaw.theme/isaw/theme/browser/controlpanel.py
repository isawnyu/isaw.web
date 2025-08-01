from .interfaces import IISAWSettings
from plone.app.registry.browser import controlpanel
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget



class ISAWSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IISAWSettings
    label = "ISAW Settings"
    description = "Custom settings for ISAW web site."

    def updateFields(self):
        super(ISAWSettingsEditForm, self).updateFields()
        self.fields['emergency_message'].widgetFactory = WysiwygFieldWidget
        self.fields['no_results_message'].widgetFactory = WysiwygFieldWidget

        self.groups[0].fields['footer_html'].widgetFactory = WysiwygFieldWidget
        self.groups[0].fields['column_one'].widgetFactory = WysiwygFieldWidget
        self.groups[0].fields['column_two'].widgetFactory = WysiwygFieldWidget
        self.groups[0].fields['disclaimer'].widgetFactory = WysiwygFieldWidget


class ISAWSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ISAWSettingsEditForm
