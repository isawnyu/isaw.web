from Acquisition import aq_inner
from zope.interface import implementer

from Products.Five.browser import BrowserView

from isaw.theme.portlets.interfaces import IFeaturePortletImageView


@implementer(IFeaturePortletImageView)
class ImageView(BrowserView):
    '''
    View the image field of the image portlet. We steal header details
    from zope.app.file.browser.file and adapt it to use the dublin
    core implementation that the Image object here has.
    '''


    def __call__(self):
        context = aq_inner(self.context)
        image = context.image
        if isinstance(image, basestring):
            return image
        return image.index_html(self.request, self.request.response)
