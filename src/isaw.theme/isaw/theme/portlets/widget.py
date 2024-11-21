from OFS.Image import Image

from zope.app.form.browser.textwidgets import FileWidget
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile


class ImageWidget(FileWidget):
    """
    The standard FileWidget returns a string instead of an IFile inst,
    which means it will always fail schema validation in formlib.
    """

    template = ViewPageTemplateFile('inputwidget.pt')
    displayWidth = 30

    def __call__(self):
        value=self._getFormValue() or None
        return self.template(name=self.context.__name__, value=value)

    def _toFieldValue(self, input):
        value=super(ImageWidget, self)._toFieldValue(input)
        if value is not self.context.missing_value:
            value=Image('image','image', value)
        return value

    def hasInput(self):
        return ((self.name+".used" in self.request.form)
                or
                (self.name in self.request.form)
                ) and not self.request.form.get(self.name+".nochange", '')
